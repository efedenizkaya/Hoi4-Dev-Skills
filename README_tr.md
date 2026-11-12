# Hoi4-Dev-Skills (Türkçe)

[English](README.md)

> **Durum: kullanılabilir.** HOI4 1.19.4.1 ("Operation Postern") için doğrulandı. Değişiklik geçmişi: [CHANGELOG.md](CHANGELOG.md).

Yapay zekâ kodlama asistanlarının (Claude Code, Codex, Cursor, Gemini CLI,
OpenCode, ZCode…) **Hearts of Iron IV** modlarını doğru yazmasını sağlayan,
oyun verisinden türetilmiş doğrulanmış Agent Skill ve araç takımı.

## Neden farklı

- **Wikiden kopyalanmış değil, oyundan türetilmiş.** Referans verisi,
  oyunun kendi sürüm damgalı dokümantasyon dosyalarından kullanıcının
  makinesinde çıkarılır — kurulu yamaya her zaman güncel. Depoya oyun
  verisi commit edilmez.
- **Doğrulama içinde.** Statik mod validator'ı, `error.log` triyaj aracı
  ve "-debug ile aç, hataları diff'le" akışı. Skill, kanıt olmadan
  "çalışıyor" demeyi reddeder.
- **Dürüst iddialar.** Oyun davranışına dair her katı iddia
  [docs/claims-register.md](docs/claims-register.md)'de kaynağa bağlı —
  168 iddia, doğrulanmamışlar açıkça etiketli.
- **Gerçek modla test edildi.** Başarısızlık nüfusu:
  [docs/dogfood-lessons.md](docs/dogfood-lessons.md).
- **MIT.** CC lisanslı alternatiflerin aksine forklayıp gömebilirsin.

## Hızlı başlangıç

```bash
git clone https://github.com/efedenizkaya/Hoi4-Dev-Skills.git
cd Hoi4-Dev-Skills
./install.sh                                   # Windows: install.ps1
python tools/extract.py                        # kendi oyunundan veri çıkar
python tools/validate.py <mod_klasoru>         # statik mod kontrolü
python tools/doctor.py --mod <mod_klasoru>     # tam sağlık raporu + skor
```

Adım adım anlatım: [docs/tutorial.md](docs/tutorial.md) (İngilizce).

## Skill

`skills/hoi4-modding/` — [Agent Skills](https://agentskills.io) standardına
uyumlu: router + 27 referans + 6 kit (event, decision, focus, ideas,
characters, scripted GUI) + iddia kaydı. Kurulum detayları:
[docs/INSTALLATION.md](docs/INSTALLATION.md).

## Araçlar

| Araç | İş |
|---|---|
| `extract.py` | oyunun makine-üretimi dokümanları → sürüm damgalı JSON |
| `validate.py` | statik lint + sessiz-hata kuralları (`--data` ile isim kontrolü) |
| `error_triage.py` | error.log sınıflandırma ve iki koşu arası diff |
| `doctor.py` | tek komutta tam sağlık raporu + 0-100 skor |
| `find.py` | identifier arama (id → dosya:satır, vanilla dahil) |
| `chain_map.py` | hangi event kimi tetikliyor (zincir grafiği) |
| `override_audit.py` | vanilla'yı birebir ezen dosyalar |
| `loc_report.py` | diller arası çeviri kapsamı |
| `loc_sync.py` | eksik çeviri iskeleti üretici (kullanıcı dosyalarına dokunmaz) |
| `chain_map.py` | event tetikleme grafiği + ölü hedefler |
| `stale_check.py` | oyun sürümü ↔ skill sürümü bayatlık kontrolü |
| `version_diff.py` | yama göçü diff'i |
| `new_mod.py` | mod iskeleti üretici |

## Katkı

Fork ve PR'lere açığız — altın kural: oyun davranışına dair her iddia
kaynaklı olmak zorunda. [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

## Lisans

[MIT](LICENSE)
