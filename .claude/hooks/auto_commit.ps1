$status = git status --porcelain 2>&1
if ($status) {
    $null = & .venv\Scripts\python.exe -m pytest services/ -x -q --ignore=services/cv/tests/test_detector.py 2>&1
    if ($LASTEXITCODE -eq 0) {
        git add -A
        git commit -m "auto: commit session changes"
        git push origin main 2>&1 | Out-Null
        Write-Output '{"systemMessage":"Auto-committed and pushed."}'
    } else {
        Write-Output '{"systemMessage":"Auto-commit skipped: tests failed. Fix before pushing."}'
    }
}
