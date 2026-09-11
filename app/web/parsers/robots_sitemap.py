import xml.etree.ElementTree as ET
from typing import Any


class RobotsSitemapParser:
    """Parses standard robots.txt and sitemap.xml."""
    
    def parse_robots(self, text: str) -> dict[str, Any]:
        result: dict[str, Any] = {
            "user_agents": [],
            "allows": [],
            "disallows": [],
            "sitemaps": []
        }
        
        current_agent = "*"
        
        for line in text.splitlines():
            line = line.split("#")[0].strip()
            if not line:
                continue
                
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip().lower()
                val = val.strip()
                
                if key == "user-agent":
                    current_agent = val
                    if val not in result["user_agents"]:
                        result["user_agents"].append(val)
                elif key == "allow":
                    result["allows"].append({"agent": current_agent, "path": val})
                elif key == "disallow":
                    result["disallows"].append({"agent": current_agent, "path": val})
                elif key == "sitemap":
                    result["sitemaps"].append(val)
                    
        return result
        
    def parse_sitemap(self, xml_text: str) -> list[dict[str, str]]:
        urls = []
        try:
            root = ET.fromstring(xml_text)
            # Handle XML namespaces which are typical in sitemaps
            ns = ""
            if "}" in root.tag:
                ns = root.tag.split("}")[0] + "}"
                
            for url_node in root.findall(f"{ns}url"):
                entry = {}
                loc = url_node.find(f"{ns}loc")
                if loc is not None and loc.text:
                    entry["loc"] = loc.text
                lastmod = url_node.find(f"{ns}lastmod")
                if lastmod is not None and lastmod.text:
                    entry["lastmod"] = lastmod.text
                if entry:
                    urls.append(entry)
        except Exception:
            pass
            
        return urls

robots_sitemap_parser = RobotsSitemapParser()
