# Validation

Validated on Windows on 2026-10-09 in an isolated project environment:

- Fresh frontend dependency installation and production build passed.
- Eight backend tests passed: health/capabilities, CORS preflight, persona round trip, material-category scan/delete, template CRUD, ungated community composition validation, retained local API-token protection and real FFmpeg composition.
- The FFmpeg test generated two synthetic clips, combined them with a title/subtitles, and verified a playable video stream with dimensions 720 x 1280. It used no customer footage.
- Python compilation and Electron entry-point syntax checks passed.
- UI demonstration screenshots use separate fictional data.

Not accepted in this release: live AI-provider replies, platform login/final posting, signed installer builds, installer upgrade/data migration or broad real-media/device compatibility. A successful synthetic composition does not establish campaign quality or all-format support.

Dependency binaries and the locally used FFmpeg runtime are excluded from the public source archive.
