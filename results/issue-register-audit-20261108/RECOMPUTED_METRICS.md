# Recomputed evidence — 8 November 2026

Raw responses and accepted labels were read without modifying them. No GPU inference was performed.

| Model | Forget correct ordinary / INT4 | Utility correct ordinary / INT4 | Mean item-mean forget NLL change | Truncated ordinary / INT4 |
| --- | --- | --- | ---: | --- |
| full | 16/20 / 16/20 | 42/60 / 39/60 | +0.016648 | 0 / 1 |
| retain90 | 3/20 / 2/20 | 51/60 / 47/60 | +0.002018 | 0 / 0 |
| simnpo_candidate | 2/20 / 2/20 | 45/60 / 43/60 | +0.032497 | 1 / 2 |

NLL change is INT4 minus ordinary. Positive means the reference answer receives lower length-normalized likelihood, not higher. It is not a correctness label.

## Short-context cache exposure

The archived cache quantizes the full prompt immediately even when it is shorter than residual_length=128. Prefill returns original tensors. Subsequent decode calls read the reconstructed prompt prefix; new decode tokens stay in the full-precision residual during these <=64-token outputs. Thus 128 is not a minimum prompt length before quantization begins.

For prompt length P and decode call t (starting at t=1), the fraction of attended positions from reconstructed quantized storage is P/(P+t). Prefill itself has fraction zero. These source-derived fractions count positions, not their attention weights, and do not measure accumulated quantization error.

| Model | Prompt tokens | Minimum decode position share | Mean over decode calls | Maximum |
| --- | --- | ---: | ---: | ---: |
| full | 48–70 | 46.6% | 78.5% | 98.6% |
| retain90 | 48–70 | 45.0% | 77.9% | 98.6% |
| simnpo_candidate | 48–70 | 47.4% | 77.0% | 98.6% |

This corrects the concern that short prompts necessarily leave the quantized cache inactive. A runtime per-step storage/flush trace remains useful for other residual settings; this calculation is not a replacement for that trace.
