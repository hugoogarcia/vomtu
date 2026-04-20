import re

with open('/Users/hugogarcia/Desktop/Vomtu/index.html', 'r', encoding='utf-8') as f:
    content = f.text if hasattr(f, 'text') else f.read()

# Add reveal-up to the main Hero elements
content = re.sub(r'(<h1.*?class=")(.*?)(">)', r'\1\2 reveal-up\3', content)
content = re.sub(r'(<p class="font-body text-lg sm:text-xl md:text-2xl.*?")', r'\1 reveal-up delay-200', content)
content = re.sub(r'(<div class="flex flex-col sm:flex-row gap-4 sm:gap-6 mb-20.*?")', r'\1 reveal-up delay-300', content)
content = re.sub(r'(<div class="flex flex-wrap justify-center gap-6">)', r'<div class="flex flex-wrap justify-center gap-6 reveal-up delay-400">', content)

# Add reveal-up to section headers (h2)
content = re.sub(r'(<h2.*?class=")(.*?)(")', r'\1\2 reveal-up\3', content)

# Add reveal-scale to all glass-panels and liquid-cards (except the button in hero)
content = re.sub(r'(<div class="liquid-card.*?")', r'\1 reveal-scale', content)
content = re.sub(r'(<div class="glass-panel.*?")', r'\1 reveal-scale', content)

# Exclude hero's 'Ver ejemplos' from global glass-panel delay, we already animated its parent.

# Add reveal-up to list items (li) in price sections
content = re.sub(r'(<li class="flex items-center gap-4 text-on-surface-variant.*?")', r'\1 reveal-up', content)
content = re.sub(r'(<li class="flex items-center gap-4 text-white.*?")', r'\1 reveal-up', content)

# Add reveal-up to FAQ details
content = re.sub(r'(<details class="group">)', r'<details class="group reveal-up">', content)

with open('/Users/hugogarcia/Desktop/Vomtu/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Hero and structural elements animated.")
