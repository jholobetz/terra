import json
import os
import glob

class HubBuilder:
    def __init__(self, content_dir="app/config/content"):
        self.content_dir = content_dir
        self.manifest_dir = "hub_manifests"

    def build_from_manifest(self, manifest_path):
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
            
        topic_slug = os.path.basename(manifest_path).replace(".json", "")
        topic_path = os.path.join(self.content_dir, "topics", f"{topic_slug}.json")
        
        # Load or create topic shard
        if os.path.exists(topic_path):
            with open(topic_path, "r") as f:
                topic_data = json.load(f)
        else:
            topic_data = {"title": manifest["title"]}

        # Update metadata
        metadata = manifest.get("metadata", {})
        topic_data["intro"] = metadata.get("intro", "")
        topic_data["field"] = metadata.get("field", "")
        topic_data["density"] = metadata.get("density", "")
        topic_data["bridges"] = metadata.get("bridges", {})
        topic_data["pillars"] = manifest.get("pillars", [])
        
        # Clear static content to force dynamic view
        topic_data["content"] = ""

        with open(topic_path, "w") as f:
            json.dump(topic_data, f, indent=4)
        print(f"SUCCESS: Platinum Hub Standard applied to [{topic_slug}]")

    def run_all(self):
        manifests = glob.glob(os.path.join(self.manifest_dir, "*.json"))
        if not manifests:
            print("No manifests found in hub_manifests/")
            return
            
        for manifest in manifests:
            self.build_from_manifest(manifest)

if __name__ == "__main__":
    builder = HubBuilder()
    builder.run_all()
