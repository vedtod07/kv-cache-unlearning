class QuantizedLayer(DynamicLayer):
    """
    A quantized layer similar to what is described in the [KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache paper](https://huggingface.co/papers/2402.02750).
    It allows the model to generate longer sequence length without allocating too much memory for the key and value caches by
    applying quantization.

    The cache has two types of storage, one for original precision and one for the quantized cache. A `residual length`
    is set as a maximum capacity for the original precision cache. When the length goes beyond maximum capacity, the original
    precision cache is discarded and moved into the quantized cache. The quantization is done per-channel with a set `q_group_size`
    for both Keys and Values, in contrast to what was described in the paper.
    """

    def __init__(
        self,
        nbits: int = 4,
        axis_key: int = 0,
        axis_value: int = 0,
        q_group_size: int = 64,
        residual_length: int = 128,
    ):
        super().__init__()
        self.nbits = nbits
        self.axis_key = axis_key
        self.axis_value = axis_value
        self.q_group_size = q_group_size
        self.residual_length = residual_length
        self.cumulative_length = 0

    def update(
        self, key_states: torch.Tensor, value_states: torch.Tensor, *args, **kwargs
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Update the key and value caches in-place, and return the necessary keys and value states.

        Args:
            key_states (`torch.Tensor`): The new key states to cache.
            value_states (`torch.Tensor`): The new value states to cache.

        Returns:
            tuple[`torch.Tensor`, `torch.Tensor`]: The key and value states.
        """
        self.cumulative_length += key_states.shape[-2]

        # Lazy initialization
        if not self.is_initialized:
            self.lazy_initialization(key_states, value_states)
            self._quantized_keys = self._quantize(key_states.contiguous(), axis=self.axis_key)
            self._quantized_values = self._quantize(value_states.contiguous(), axis=self.axis_value)
            return key_states, value_states

        dequant_keys = self._dequantize(self._quantized_keys)
        dequant_values = self._dequantize(self._quantized_values)
        keys_to_return = torch.cat([dequant_keys, self.keys, key_states], dim=-2)
        values_to_return = torch.cat([dequant_values, self.values, value_states], dim=-2)
        if self.keys.dim() == 4 and self.keys.shape[-2] + 1 >= self.residual_length:
            self._quantized_keys = self._quantize(keys_to_return.contiguous(), axis=self.axis_key)
            self._quantized_values = self._quantize(values_to_return.contiguous(), axis=self.axis_value)
            self.keys = torch.tensor([], dtype=key_states.dtype, device=key_states.device)
            self.values = torch.tensor([], dtype=key_states.dtype, device=key_states.device)
        else:
            self.keys = torch.cat([self.keys, key_states], dim=-2)
            self.values = torch.cat([self.values, value_states], dim=-2)

        return keys_to_return, values_to_return

    @abstractmethod
    def _quantize(self, tensor, axis): ...

    @abstractmethod
    def _dequantize(self, q_tensor): ...

    def get_seq_length(self) -> int:
        """Returns the sequence length of the cached states."""
        return self.cumulative_length
