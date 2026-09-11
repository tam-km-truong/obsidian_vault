```bash
sed 's|^|fasta/|' ls_fasta.txt | xargs -d '\n' du -sb | awk -v total=715000 '
BEGIN {
    start_time = systime();
}
{
    sum += $1;
    if (NR % 10000 == 0) {
        current_time = systime();
        elapsed = current_time - start_time;
        
        # Avoid division by zero
        if (elapsed > 0) {
            rate = NR / elapsed; # folders per second
            remaining = (total - NR) / rate;
            
            # Format remaining time into HH:MM:SS
            hours = int(remaining / 3600);
            mins = int((remaining % 3600) / 60);
            secs = int(remaining % 60);
            
            printf "Progress: %d/%d (%.1f%%) | Total: %d bytes | ETR: %02d:%02d:%02d\n", 
                   NR, total, (NR/total)*100, sum, hours, mins, secs
        } else {
            printf "Progress: %d/%d (%.1f%%) | Total: %d bytes | ETR: Calculating...\n", 
                   NR, total, (NR/total)*100, sum
        }
    }
} 
END {
    final_time = systime();
    printf "--- FINISHED ---\nTotal Folders: %d\nGrand Total: %d bytes\nTime Taken: %d seconds\n", 
           NR, sum, final_time - start_time
}'
```