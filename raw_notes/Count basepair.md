
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