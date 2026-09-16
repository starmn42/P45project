# LZ76 IMPLEMENTATION NOTE

- locked execution orchestrator: `lz76_locked_execution.py`
- independent Python reference/calculator: `lz76_calculator.py`
- compiled scorer source/assembly: `Lz76Scorer.cs`, `Lz76Scorer.dll`
- locked definition: shortest substring at the current position absent from the processed prefix; incomplete final suffix counts as one phrase.
- production implementation: locally compiled C# online binary suffix automaton representing every substring of the processed prefix. At each phrase boundary it finds the longest prefix of the remaining suffix present in that automaton; the next phrase is that match plus one bit, or the complete remaining suffix at end-of-string.
- independent reference: direct substring-set membership implementation, used only on short synthetic inputs.
- external LZ package: none.
- primary normalization: `c(4500) * log2(4500) / 4500` only.
- RNG: NumPy `Generator(PCG64)`.
- fair 6/45 generation: for every draw, generate 45 i.i.d. continuous PCG64 priorities and select the six smallest. By exchangeability this is a uniform six-element subset without replacement.
- Python/NumPy generates every uniform subset in one continuous locked PCG64 stream. The compiled scorer only reads already generated bits. Parallelism changes execution speed only and each output is stored at its original row index.
- result isolation: no Fixed, Linked, Consensus, NUMBER, TRIO, PAIR, CORE, KTS45, hit rate, number-level, or subgroup calculation exists in the calculator.
