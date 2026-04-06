MATERIAL_CHOICES = {
    "ОТ4": "ОТ4 - Титановый сплав",
    "ВТ6": "ВТ6 / ВТ-6 / ВТ6С - Титановый сплав Ti-6Al-4V",
    "ЭП741НП": "ЭП741НП - Жаропрочный никелевый сплав",
}

class PlasmaOptimizer:
    def __init__(self, plasma):
        self.plasma = plasma

    def _normalize(self, s: str) -> str:
        return s.strip().upper().replace("-", "").replace(" ", "")

    def define_material(self, material_type: str) -> str:
        if not material_type:
            raise ValueError("Material type cannot be empty.")
        normalized_type = self._normalize(material_type)
        
        for key, description in MATERIAL_CHOICES.items():
            if self._normalize(key) == normalized_type:
                return description
        raise ValueError(f"Unknown material type: {material_type}")        


a = PlasmaOptimizer("ВТ6")
print(a.define_material("ЭП741НП"))