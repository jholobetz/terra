import json

with open('hub_manifests/classical-mechanics.json', 'r') as f:
    manifest = json.load(f)

with open('app/config/content/classical-mechanics.json', 'r') as f:
    content = json.load(f)

all_slugs = []
for pillar in manifest['pillars']:
    all_slugs.extend(pillar['slugs'])

results = []
for slug in all_slugs:
    if slug in content:
        results.append((slug, content[slug].get('standard', 'unknown')))
    else:
        results.append((slug, 'MISSING'))

platinum = [s for s, st in results if st == 'platinum']
legacy = [s for s, st in results if st == 'legacy']
missing = [s for s, st in results if st == 'MISSING']

print(f"Total Slugs in Manifest: {len(all_slugs)}")
print(f"Platinum: {len(platinum)}")
print(f"Legacy: {len(legacy)}")
print(f"Missing: {len(missing)}")

print("\nLegacy Slugs:")
for s in legacy:
    print(f" - {s}")

print("\nMissing Slugs:")
for s in missing:
    print(f" - {s}")
