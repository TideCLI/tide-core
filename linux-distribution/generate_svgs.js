const fs = require('fs');
const path = require('path');

const IMAGES_DIR = path.join(__dirname, 'public/images');
if (!fs.existsSync(IMAGES_DIR)) {
    fs.mkdirSync(IMAGES_DIR, { recursive: true });
}

const images = [
    'hero',
    'dashboard',
    'terminal',
    'architecture',
    'tide-cli',
    'preview-1',
    'preview-2',
    'preview-3'
];

images.forEach(name => {
    const content = `
<svg width="800" height="450" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#F8FAFC"/>
  <rect x="40" y="40" width="720" height="370" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="2" rx="8"/>
  <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="40" fill="#334155" text-anchor="middle" font-weight="bold">${name.toUpperCase()}</text>
  <text x="50%" y="60%" font-family="Arial, sans-serif" font-size="20" fill="#64748B" text-anchor="middle">Mockup Placeholder</text>
</svg>
`;
    fs.writeFileSync(path.join(IMAGES_DIR, `${name}.svg`), content.trim());
    console.log(`Generated ${name}.svg`);
});
