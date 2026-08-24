# Turbo.az Nissan Sunny Bildiriş Botu

Bu bot turbo.az saytında yeni Nissan Sunny elanı yerləşəndə Telegram-a bildiriş göndərir.
Hər 10 dəqiqədən bir GitHub Actions vasitəsilə avtomatik işə düşür — sənin kompüterin
açıq olmasına ehtiyac yoxdur.

## Qurulum (bir dəfəlik, 10-15 dəqiqə)

### 1. GitHub hesabı yarat (yoxdursa)
https://github.com/signup

### 2. Yeni repository yarat
- github.com-da sağ yuxarıda "+" → "New repository"
- Adı: `turbo-az-bot` (istənilən ad ola bilər)
- **Private** seç (tövsiyə olunur)
- "Create repository"

### 3. Faylları yüklə
Bu qovluqdakı fayllar (`check_turbo.py`, `.github/workflows/check.yml`, `README.md`) repo-ya yüklənməlidir:
- Repo səhifəsində "Add file" → "Upload files"
- Bütün faylları (qovluq strukturunu saxlayaraq) sürüşdür-burax
- "Commit changes"

**QEYD:** `.github/workflows/check.yml` faylının məhz bu qovluq strukturunda olması vacibdir
(`.github/workflows/` qovluğu daxilində). GitHub-un veb interfeysi ilə qovluq yükləmək bəzən
çətin ola bilər — bu halda "Create new file" düyməsi ilə əl ilə `.github/workflows/check.yml`
yazıb, içinə bu faylın məzmununu yapışdıra bilərsən.

### 4. Token və Chat ID-ni "Secrets" olaraq əlavə et
Repo səhifəsində:
- Settings → Secrets and variables → Actions → "New repository secret"
- 1-ci secret: Name = `TELEGRAM_BOT_TOKEN`, Value = sənin bot tokenin
- 2-ci secret: Name = `TELEGRAM_CHAT_ID`, Value = `848837342`

Bu üsulla token kodun içində açıq görünmür.

### 5. İlk işə salınma
- Repo-da "Actions" bölməsinə keç
- "Turbo.az Nissan Sunny Bildiriş" workflow-unu seç
- "Run workflow" düyməsinə bas (əl ilə ilk dəfə işə salmaq üçün)

**Vacib:** ilk işə salınmada bot bildiriş GÖNDƏRMİR — mövcud bütün elanları "artıq görülüb"
kimi qeyd edir. Bundan sonrakı işə salınmalarda YALNIZ yeni əlavə olunan elanlar üçün
bildiriş gələcək.

### 6. Hazırdır!
Bundan sonra hər 10 dəqiqədən bir avtomatik işləyəcək və yeni Nissan Sunny elanı
olanda Telegram-a bildiriş göndərəcək.

## Filtrləri dəyişmək istəsən

`check_turbo.py` faylının başındakı CONFIG bölməsində:
- `MODEL_KEYWORD` — başqa model axtarmaq üçün (məs: "almera", "tiida")
- `MIN_YEAR`, `MAX_YEAR` — il aralığı
- `MIN_PRICE`, `MAX_PRICE` — qiymət aralığı (hazırkı versiyada bu iki filtr strukturu
  hazırdır, amma aktiv istifadə üçün əlavə kodlaşdırma lazımdır — mənə yaz, əlavə edim)

## Problemi həll etmə

- **Bildiriş gəlmir:** Actions tabında son işə salınmanın loqlarına bax (yaşıl ✓ və ya qırmızı ✗
  işarəsinə klik et) — xəta mesajı orda görünəcək.
- **"seen_ids.json" push xətası:** repo-nun Settings → Actions → General bölməsində
  "Workflow permissions" → "Read and write permissions" seçili olmalıdır.
