# OLMo – Open Language Model (Ai2)

**OLMo** je rodina jazykových modelov od **Allen Institute for AI (Ai2)**. Od väčšiny „open-weight“ modelov (Llama, Qwen, Mistral) sa líši tým, že je **úplne otvorený**: okrem váh sú zverejnené aj **trénovacie dáta**, trénovací kód, **checkpointy** z rôznych fáz tréningu, logy a evaluácie. Licencia je **Apache 2.0**. Preto sú na ňom v tomto školení ukázané konkrétne čísla. Pojmy sú v [slovníku](slovnik.md).

## Verzie

| Verzia | Dátum | Veľkosti | Poznámka |
|---|---|---|---|
| OLMo 1 | 02/2024 | 1B, 7B | ~2,5T tokenov |
| OLMoE | 09/2024 | 7B MoE (1B aktívnych) | Mixture of Experts |
| OLMo 2 | 11/2024 – 03/2025 | 1B, 7B, 13B, 32B | 4–6T tokenov, kontext 4k |
| OLMo 3 / 3.1 | 11–12/2025 | 7B, 32B (Base, Instruct, Think, RL-Zero) | ~6T tokenov, kontext 65k, sliding window |
| Olmo Hybrid | 03/2026 | 7B | transformer + lineárne RNN vrstvy |

## Topológia

Decoder-only transformer so SwiGLU, RoPE, RMSNorm a QK-norm, bez biasov v lineárnych vrstvách. Ako vyzerá jeden blok a kde sú parametre, popisuje [transformer-topology.md](2_transformer-topology.md).

| Model | Vrstvy | d_model | Attention hlavy (Q / KV) | FFN (SwiGLU) | Kontext |
|---|---|---|---|---|---|
| OLMo 2 1B | 16 | 2048 | 16 / 16 | 8192 | 4k |
| OLMo 2 7B | 32 | 4096 | 32 / 32 | 11 008 | 4k |
| OLMo 2 13B | 40 | 5120 | 40 / 40 | 13 824 | 4k |
| OLMo 2 32B | 64 | 5120 | 40 / 8 (GQA) | 27 648 | 4k |
| OLMo 3 7B | 32 | 4096 | 32 / 32 | 11 008 | 65k |
| OLMo 3 32B | 64 | 5120 | 40 / 8 (GQA) | 27 648 | 65k |

*Zdroj: `config.json` modelov na Hugging Face. Veľkosť hlavy je všade 128, slovník ~100k tokenov. OLMo 3 strieda 3 vrstvy so sliding-window attention (okno 4096) a 1 vrstvu s plnou attention.*

## Porovnanie s malým a veľkým modelom

Tri body na škále: malý Llama na notebook, stredný OLMo a frontier open-weight DeepSeek.

| Model | Typ | Vrstvy | d_model | Hlavy (Q / KV) | FFN | Slovník | Kontext | Parametre |
|---|---|---|---|---|---|---|---|---|
| Llama 3.2 1B | dense | 16 | 2048 | 32 / 8 (GQA) | 8192 | 128 256 | 128k | 1,24B |
| Llama 3.1 8B | dense | 32 | 4096 | 32 / 8 (GQA) | 14 336 | 128 256 | 128k | 8,0B |
| OLMo 2 7B | dense | 32 | 4096 | 32 / 32 | 11 008 | ~100k | 4k | 7,3B |
| OLMo 3 32B | dense | 64 | 5120 | 40 / 8 (GQA) | 27 648 | ~100k | 65k | 32B |
| DeepSeek LLM 67B (2024) | dense | **95** | 8192 | 64 / 8 (GQA) | 22 016 | 102 400 | 4k | 67B |
| DeepSeek-V3 / R1 | MoE | 61 | 7168 | 128 (MLA) | 18 432 dense / 2048 expert | 129 280 | 128k | **671B (37B aktívnych)** |

*Najhlbší v tabuľke je **DeepSeek LLM 67B** z januára 2024 s 95 vrstvami. Dnešný DeepSeek-V3/R1 má iba 61 vrstiev, ale je **MoE**: 3 dense vrstvy a 58 MoE vrstiev s 256 expertmi + 1 zdieľaným, z ktorých sa na token aktivuje 8.*

### Ako sa počet parametrov vypočíta

Pre jeden dense blok (SwiGLU FFN, GQA attention, veľkosť hlavy *h*):

```
attention = d_model × (n_q·h)  +  2 × d_model × (n_kv·h)  +  (n_q·h) × d_model
FFN       = 3 × d_model × d_ff          (W_gate, W_up, W_down)
model     = vrstvy × (attention + FFN)  +  slovník × d_model × (1 alebo 2)
```

Posledný člen je embedding tabuľka a LM head: ×1 ak sú **zdieľané** (tied, malé modely), ×2 ak sú samostatné. Normalizácie sú zanedbateľné.

**Llama 3.2 1B** (d=2048, 32 Q hláv a 8 KV hláv, h=64, 16 vrstiev, tied embedding):
- attention = 2048×2048 + 2×2048×512 + 2048×2048 = **10,5M** (n_q·h = 32×64 = 2048, n_kv·h = 8×64 = 512)
- FFN = 3 × 2048 × 8192 = **50,3M**
- vrstvy = 16 × 60,8M = **973M**, embedding = 128 256 × 2048 = **263M**
- spolu ≈ **1,24B**

**OLMo 2 7B** (d=4096, MHA, 32 vrstiev, netied):
- attention = 4 × 4096² = **67M**, FFN = 3 × 4096 × 11 008 = **135M**
- vrstvy = 32 × 202M = **6,5B**, embedding + head = 2 × 100 352 × 4096 = **0,8B**
- spolu ≈ **7,3B**

**DeepSeek-V3** (d=7168, MLA, 61 vrstiev) – pri MoE sa FFN počíta za každého experta:
- attention (MLA s kompresiou Q a KV) ≈ **187M** na vrstvu
- 3 dense vrstvy: FFN = 3 × 7168 × 18 432 = 396M → ≈ **1,8B**
- 58 MoE vrstiev: jeden expert = 3 × 7168 × 2048 = 44M; 256 routed + 1 zdieľaný = 257 × 44M ≈ **11,3B** na vrstvu, s attention 58 × (11,3B + 0,19B) ≈ **668B**
- embedding + head = 2 × 129 280 × 7168 ≈ **1,9B**
- spolu ≈ **671B**; na jeden token sa však použije iba 8 routed + 1 zdieľaný expert, teda ≈ **37B aktívnych**

### Čo z toho vyplýva

- **Hĺbka (vrstvy) a šírka (d_model) rastú pomaly, parametre rýchlo.** Z 1B na 671B je to 540×, ale vrstiev je len 4× viac a d_model 3,5× viac. Parametre dense modelu rastú s *vrstvy × d_model²*, takže aj mierne rozšírenie pridá veľa parametrov. Zvyšok rozdielu pri DeepSeeku spraví MoE (veľa expertov v každej vrstve).
- **FFN je dominantná položka** (~2/3 parametrov dense modelu), preto MoE šetrí práve tam.
- **GQA je dnes štandard pri väčších modeloch.** OLMo 2 7B aj OLMo 3 7B majú ešte plnú MHA. OLMo 32B a Llama používajú 8 KV hláv, DeepSeek-V3 kompresiu KV (MLA), všetko kvôli veľkosti KV cache pri dlhom kontexte.
- **MoE mení pomer pamäte a výpočtu.** DeepSeek-V3 potrebuje v pamäti ~671B parametrov (~700 GB v 8 bitoch; nezmestí sa ani do uzla s 8× H100, ktorý má 8 × 80 = 640 GB, treba napríklad 8× H200 alebo dva uzly), ale počíta ako 37B model. Dense OLMo 32B potrebuje ~64 GB a počíta ako 32B.
- **Kontext nie je parameter.** Llama 1B má 128k kontext a 1,24B parametrov; dĺžka kontextu neovplyvní počet váh, len pamäť KV cache pri inferencii.

## Koľko stojí tréning

Model sa trénoval na klastroch s **NVIDIA H100**, naraz až na **1024 GPU**. Hrubý odhad cez pravidlo **FLOPs ≈ 6 × parametre × tokeny** ukazuje, prečo to na jednej GPU nejde:

| Model | Výpočet | 1× H100 | 1× RTX 4090 | 1024× H100 |
|---|---|---|---|---|
| 7B, 6T tokenov | ~2,5·10²³ FLOPs | ~25 rokov | ~130 rokov | ~9 dní |
| 32B, 6T tokenov | ~1,2·10²⁴ FLOPs | ~100 rokov | ~600 rokov | ~1,5 mesiaca |

Okrem času naráža plný tréning aj na pamäť: ~16 B na parameter (váhy, gradienty a stavy Adamu), teda 7B model potrebuje 110 GB+. Na bežnej GPU dáva zmysel iba **fine-tuning cez LoRA/QLoRA**, ktorý pri 7B modeli trvá hodiny.

### Trvanie fáz tréningu

Skutočné čísla pre **OLMo 3 32B (Think)** z technického reportu Ai2. Fázy v tabuľke dávajú spolu **~54 dní** na 1024 GPU, pri cene 2 $ za hodinu H100 by to stálo **~2,7 mil. $**.

| Fáza | Dáta | Trvanie |
|---|---|---|
| Pretraining | ~5,9T tokenov | ~44,5 dňa |
| Mid-training | 100B tokenov | ~1,5 dňa |
| Long-context rozšírenie | 100B tokenov | ~1 deň |
| **Základný tréning spolu** | | **~47 dní** |
| SFT | ~2 mil. príkladov | 36 hodín |
| DPO | ~150 tis. párov odpovedí | ~18 hodín |
| RLVR | matematika, kód, pokyny | ~5 dní |
| **Post-training spolu** | | **~7 dní** |

- **Základný tréning tvorí väčšinu času aj výpočtu.** Model sa v ňom naučí jazyk, fakty a schopnosti.
- **Instruction tréning (SFT + DPO) je krátky.** Model sa v ňom nič zásadne nové nenaučí, len formát konverzácie, plnenie pokynov a štýl.
- **RL pri reasoning modeloch môže byť dlhé.** Pri OLMo 3.1 sa predĺžilo o ďalšie 3 týždne, lebo model sa stále zlepšoval. Väčšinu času tu zaberá generovanie dlhých odpovedí, nie samotná úprava váh.

## Na akých dátach sa trénuje

Dataset **Dolma 3** (pool ~9T tokenov, na pretraining sa použije ~6T): filtrovaný web (Common Crawl), vedecké články, kód z GitHubu, matematika, Wikipedia a knihy. Na konci tréningu nasleduje menšia, kvalitnejšia zmes (mid-training) a potom post-training dáta pre SFT, DPO a RLVR.

## Porovnanie výkonu

| Model | Rok | Zhruba |
|---|---|---|
| GPT-3.5 Turbo | 2022/23 | OLMo 2 32B ho prekonáva |
| GPT-4 (pôvodný) | 03/2023 | OLMo 3 32B má o niečo menej na MMLU, v matematike a reasoningu je výrazne lepší |
| Qwen 3 32B, Llama 3.x 70B | 2025 | OLMo 3 32B Think sa im približuje |
| GPT-5.x, Claude Opus/Sonnet 4.x–5, Gemini 3 | 2025–26 | výrazne lepšie |

Za open-weight modelmi (Qwen, DeepSeek, Kimi) zaostáva OLMo približne o 6–12 mesiacov, za frontier modelmi o 1,5–2 roky. Je to však **najlepší plne otvorený model**.

## Zaujímavosti

- **OLMoTrace** dokáže k vygenerovanej odpovedi nájsť doslovné úseky z trénovacích dát. Pri iných modeloch to nie je možné.
- Zverejnené sú **stovky checkpointov** z celého tréningu, takže sa dá skúmať, ako sa model „učí“ v čase.
- **RL-Zero** varianty umožňujú študovať RL priamo na base modeli bez SFT.

Aktuálny stav je na [allenai.org/olmo](https://allenai.org/olmo) a na [huggingface.co/allenai](https://huggingface.co/allenai).

---
*Čísla o čase tréningu sú hrubé odhady. Výsledky benchmarkov sa líšia podľa verzie (base/instruct/think) a metodiky.*
