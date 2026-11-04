# Demo: Rozpoznávanie číslic — feed-forward sieť v čistom NumPy

**Kód:** [image-recognition/](image-recognition/) · **Dataset:** MNIST (28×28, 60k train / 10k test, IDX súbory v `mnist/`, nie sú v repe)

Kompletná implementácia MLP bez ML frameworku: forward, backprop, Adam, augmentácia, inferencia vlastných obrázkov a GUI na kreslenie. Závislosti: `numpy`, `Pillow`, `matplotlib`, `PyQt5`.

## Obsah

| Modul | Čo poskytuje |
|---|---|
| [loader.py](image-recognition/loader.py) | parser binárneho IDX formátu MNIST |
| [show_images.py](image-recognition/show_images.py) | vizualizácia náhodných vzoriek s labelmi |
| [feed_forward.py](image-recognition/feed_forward.py) | model, tréning, CLI |
| [inference.py](image-recognition/inference.py) | predspracovanie vlastného PNG + predikcia |
| [digit_drawer.py](image-recognition/digit_drawer.py) | PyQt5 GUI: kreslenie 280×280 → inferencia |
| [.vscode/launch.json](image-recognition/.vscode/launch.json) | hotové konfigurácie `1.`–`6.` + `train model s augmentaciou` |

## Model

- Architektúra: `784 → [128, 64] → 10` (konfigurovateľné), ~109k parametrov.
- He inicializácia ([feed_forward.py:108](image-recognition/feed_forward.py#L108)).
- Aktivácie: `relu` / `leaky_relu`; výstup softmax so stabilizáciou odčítaním maxima ([:152](image-recognition/feed_forward.py#L152)).
- Forward ([:157](image-recognition/feed_forward.py#L157)), loss + gradienty ([:173](image-recognition/feed_forward.py#L173)): cross-entropy, výstupný gradient `probs − one_hot`, spätný priechod reťazovým pravidlom.
- Adam ručne implementovaný vrátane bias correction ([:207](image-recognition/feed_forward.py#L207)).
- Mini-batch tréning ([:262](image-recognition/feed_forward.py#L262)), default batch 64.
- Validačný split (default 0.1) s hlásením overfittingu ([:303](image-recognition/feed_forward.py#L303)).
- Augmentácia batchov (viď nižšie), zapína `--augment` ([:45](image-recognition/feed_forward.py#L45)).
- Dáta: `reshape(-1, 784)`, normalizácia `/255.0` ([:425](image-recognition/feed_forward.py#L425)).
- Serializácia modelu do `.npy`; vizualizácia architektúry ([feed_forward_trained.svg](image-recognition/feed_forward_trained.svg)).

## Inferencia vlastných obrázkov

`normalize_like_mnist()` ([inference.py:19](image-recognition/inference.py#L19)) replikuje pôvodné predspracovanie MNIST:
invert → crop na bounding box → resize do 20×20 so zachovaním pomeru → vloženie do 28×28 → centrovanie podľa ťažiska.
Prepínač `--no-normalize` to vypne a slúži na demonštráciu train/serve skew.
Výstup obsahuje stĺpcový graf pravdepodobností pre všetkých 10 tried.

## CLI

```bash
python feed_forward.py [--hidden-layers 128 64] [--epochs 5] [--batch-size 64]
                       [--learning-rate 1e-3] [--beta1 0.9] [--beta2 0.999] [--epsilon 1e-8]
                       [--activation relu|leaky_relu] [--validation-split 0.1]
                       [--augment] [--train-samples N] [--seed 42] [--save-model model.npy]

python inference.py --model-path model.npy --image-path trojka.png [--no-normalize]
python show_images.py
python digit_drawer.py
```

## Referenčné výsledky

| Beh | Konfigurácia | Čas | Test accuracy |
|---|---|---|---|
| slabý | `--train-samples 500 --epochs 3 --hidden-layers 16` | ~5 s | 45,4 % |
| silný | `--epochs 5 --hidden-layers 128 64` | ~20 s | 97,4 % |
| augmentovaný | `--epochs 50 --activation leaky_relu --augment` | — | `feed_forward_trained.npy` |

Silný model, `trojka.png` (čierna číslica na bielom, necentrovaná):
`--no-normalize` → predikcia **7** (~52 %); s normalizáciou → predikcia **3** (~100 %).

## Čo demo demonštruje

- Mapovanie na PyTorch: `_forward()` ↔ `nn.Linear`+`nn.ReLU`, `_loss_and_gradients()` ↔ `nn.CrossEntropyLoss`+`loss.backward()`, `_apply_adam()` ↔ `torch.optim.Adam`, `augment_batch()` ↔ `transforms.RandomAffine`.
- Train/serve skew: 97 % na teste vs. zlyhanie na vlastnom obrázku bez identického predspracovania.
- Chýbajúca OOD detekcia: softmax rozdelí 100 % medzi 10 tried aj pre vstup, ktorý nie je číslica.
- Limity feed-forward siete oproti CNN (žiadna priestorová štruktúra, strop ~97–98 % vs. ~99,5 %).

## Augmentácia

`augment_batch()` ([feed_forward.py:45](image-recognition/feed_forward.py#L45)), parametre v `AugmentConfig`:

- Posun `±2 px` (nezávisle v oboch osiach) a rotácia `±10°`, náhodne pre každú vzorku.
- Obe transformácie sa skladajú do **jednej afinnej matice** a aplikujú **spätným mapovaním**
  (cieľový pixel → zdrojová súradnica) s **bilineárnou interpoláciou**. Jedna interpolácia namiesto
  dvoch znamená menšie rozmazanie ťahu. Mimo plátna sa dopĺňa čierna.
- Aplikuje sa **za behu na každý mini-batch**, nie raz dopredu — sieť v každej epoche vidí iné variácie
  a dataset nerastie v pamäti.
- Zmysel: zmenšiť rozdiel medzi trénovacím rozdelením a reálnymi vstupmi. Je to doplnok
  k predspracovaniu pri inferencii, nie jeho náhrada. Preto sa oplatí trénovať dlhšie
  (`--epochs 50`), model sa ťažšie preučí.
- Vedomé obmedzenie: žiadne škálovanie, shear ani elastické deformácie, žiadne horizontálne
  preklopenie (pre číslice by menilo význam triedy).

## Ako sa to rieši v praxi

**Ďalšia augmentácia:** škálovanie, shear, elastické deformácie (klasika pre MNIST), náhodné
výrezy, zmena hrúbky ťahu (morfologické operácie), `mixup` / `cutout`. V PyTorchi `transforms.RandomAffine`,
`ElasticTransform`, `RandomErasing`.

**Regularizácia:** dropout, weight decay (L2), batch/layer normalization, early stopping podľa
validačnej straty, rozvrh learning rate (cosine, step decay). V tomto deme nie je nič z toho —
jedinou poistkou je sledovanie `val_acc`.

**Konvolučné siete (CNN)** — hlavný architektonický skok a dôvod, prečo tento MLP končí na ~97–98 %:

- MLP dostáva obrázok ako **784 nezávislých čísel**. Informácia, že pixely `(5,5)` a `(5,6)` sú susedia,
  sa v `reshape(-1, 784)` stráca; sieť sa ju musí namáhavo naučiť z dát.
- Konvolučná vrstva miesto plne prepojenej matice posúva po obrázku malý **filter** (napr. 3×3) a počíta
  skalárny súčin s každým okolím. Jeden filter = jedna naučená lokálna črta (hrana, roh, oblúk).
- Dva dôsledky: **lokalita** (neurón vidí len svoje okolie) a **zdieľanie váh** (ten istý filter platí
  pre celý obrázok). Z 100 352 parametrov prvej vrstvy MLP sa stane 9 parametrov na filter — menej
  parametrov, menšie riziko preučenia a **translačná invariancia zadarmo**: črta sa rozpozná
  nezávisle od toho, kde v obrázku je. Presne tú vlastnosť, ktorú tu suplujeme centrovaním a augmentáciou.
- **Pooling** (max/average) zmenšuje rozlíšenie, zväčšuje receptívne pole a pridáva odolnosť
  voči malým posunom. Striedaním `conv → aktivácia → pooling` vzniká hierarchia:
  hrany → časti tvarov → celé číslice.
- Na konci sa feature mapy sploštia a idú do klasifikačnej hlavy — teda presne do siete,
  akú má toto demo. Backprop, cross-entropy aj Adam zostávajú **nezmenené**.
- Výsledok na MNIST: jednoduchá CNN ~99,2–99,5 % oproti ~97–98 % tu, s menším počtom parametrov.

**Ešte ďalej:** reziduálne spojenia (ResNet) pre hlboké siete, transfer learning z predtrénovaného
modelu namiesto tréningu od nuly, a Vision Transformery (obrázok ako sekvencia patchov, priestorová
štruktúra sa učí cez attention namiesto pevnej konvolučnej predpojatosti) — tie však potrebujú
rádovo viac dát alebo predtréning.

Doplnkový výklad: [softmax a cross-entropy](softmax-cross-entropy.md).

## Známe obmedzenia

- MNIST `*-ubyte` súbory sú v `.gitignore` — treba ich doplniť lokálne do `mnist/`.
- GUI vyžaduje PyQt5; bez neho je použiteľná len CLI inferencia.
- `trojka.png` si treba vytvoriť (GUI → **Uložiť PNG**), ak chýba.
