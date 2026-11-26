# Referencias oficiales para verificar antes de implementar
Consultadas el 25 de noviembre de 2026 (Perú). Revisar cambios y requisitos del validador antes de exportar o publicar.

- Recursos y plantillas R15/cages: https://create.roblox.com/docs/avatar/resources
- Blender y escala: https://create.roblox.com/docs/art/blender
- Accesorios rígidos: https://create.roblox.com/docs/avatar/rigid-accessories/specifications
- Ropa 3D por capas: https://create.roblox.com/docs/avatar/layered-accessories/specifications
- Cuerpos: https://create.roblox.com/docs/avatar/character-bodies/specifications
- Texturas: https://create.roblox.com/docs/art/modeling/texture-specifications
- Materiales PBR y máscaras emisivas: https://create.roblox.com/docs/art/modeling/surface-appearance
- Exportación: https://create.roblox.com/docs/art/modeling/export-requirements
- Exportación de ropa por capas: https://create.roblox.com/docs/avatar/layered-accessories/export
- Accessory Fitting Tool: https://create.roblox.com/docs/avatar/accessory-fitting-tool
- Avatar Setup: https://create.roblox.com/docs/avatar-setup/auto-setup-requirements
- Validación UGC: https://create.roblox.com/docs/marketplace/validation-system
- Publicación: https://create.roblox.com/docs/marketplace/publish-to-marketplace
- Políticas: https://create.roblox.com/docs/marketplace/marketplace-policy
- Tarifas: https://create.roblox.com/docs/marketplace/marketplace-fees-and-commissions
- Blender oficial: https://www.blender.org/download/
- Python oficial: https://www.python.org/downloads/
- Git oficial: https://git-scm.com/downloads
- Roblox Studio: https://create.roblox.com/

Observaciones: la documentación de rígidos y layered indica una malla por artículo y 4k triángulos; layered requiere rig R15 y cages interior/exterior. Las especificaciones generales de texturas indican 1024² como resolución soportada y las páginas de accesorios mencionan tope de 2048² para Marketplace: usar 1024² conservadoramente y comprobar el validador actual. Las máscaras emisivas se admiten en artículos de avatar según documentación PBR, pero la apariencia depende de configuración del juego y render. La publicación exige elegibilidad, moderación y puede implicar pagos; no automatizar pagos.
