---
raw_tags:
  - total
  - count
  - tar
  - grep
  - salmonella_enterica
word_count: 89
char_count: 552
processed: true
processed_note: \"[[CLI - Fast Basepair Counting]]\"
---

```bash
total=0
for f in ./*.tar.xz; do
  count=$(tar -xOf "$f" | grep -v '^>' | tr -d '\n' | wc -c)
  echo "$count $f"
  total=$((total + count))
done
echo "Total: $total"
```

```bash
total=0; for f in ./salmonella_enterica__*.tar.xz; do count=$(tar -xOf "$f" | grep -v '^>' | tr -d '\n' | wc -c); echo "$count $f"; total=$((total + count)); done; echo "Total: $total"
```