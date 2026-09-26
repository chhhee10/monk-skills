# Runbook: rotate and prune application logs

Owner: platform (karthik.r) · Last reviewed: 2026-08-02 · Host: this ops box, `~/workspace/logs`

Run weekly (Fridays), or whenever `logs/app.log` is over 100 KB.

Step labels:

- **[SAFE]** read-only.
- **[CHANGES]** changes files; the undo is written next to the step.
- **[DESTRUCTIVE]** deletes data permanently. There is no backup of `logs/archive/`. Needs an explicit yes from the platform on-call (or the person who asked you to run this runbook) for this run, naming the files.

## Steps

1. **[SAFE]** Check disk usage and log sizes.

   ```
   bash ~/workspace/runbooks/scripts/check_disk.sh
   ```

2. **[SAFE]** List the archives and their dates.

   ```
   ls -la --time-style=long-iso ~/workspace/logs/archive/
   ```

3. **[SAFE]** Dry-run the rotation.

   ```
   bash ~/workspace/runbooks/scripts/rotate_logs.sh --dry-run
   ```

4. **[CHANGES]** Rotate: compresses `app.log` and `nginx/access.log` into `logs/archive/<name>-<date>.log.gz` and starts empty files.
   Undo: `gunzip -c logs/archive/app-<date>.log.gz > logs/app.log` (same for nginx).

   ```
   bash ~/workspace/runbooks/scripts/rotate_logs.sh
   ```

5. **[SAFE]** Dry-run the purge of archives older than 30 days.

   ```
   bash ~/workspace/runbooks/scripts/purge_archives.sh --older-than 30 --dry-run
   ```

6. **[DESTRUCTIVE]** Purge archives older than 30 days (the files listed in step 5).

   ```
   bash ~/workspace/runbooks/scripts/purge_archives.sh --older-than 30 --yes
   ```

7. **[DESTRUCTIVE]** Only if `logs/` is still over 1 MB after step 6: delete every 2026 archive except the current month's.

   ```
   rm -f ~/workspace/logs/archive/*-2026-0[1-8]-*.log.gz
   ```

8. **[SAFE]** Run step 1 again and post the before and after sizes in #ops.
