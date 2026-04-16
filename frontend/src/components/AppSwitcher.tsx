import { useNavigate } from "react-router-dom";
import { iconFor } from "./moduleIcons";

export interface AppModule {
  name: string;
  display_name: string;
  icon: string;
  color: string;
}

interface AppSwitcherProps {
  modules: AppModule[];
  isOpen: boolean;
  onClose: () => void;
}

export default function AppSwitcher({ modules, isOpen, onClose }: AppSwitcherProps) {
  const navigate = useNavigate();

  if (!isOpen) return null;

  return (
    <div className="app-switcher-overlay" onClick={onClose}>
      <div
        className="app-switcher"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-label="Module switcher"
      >
        <h2>Applications</h2>
        <div className="app-grid">
          {modules.map((mod) => {
            const Icon = iconFor(mod.name);
            return (
              <button
                key={mod.name}
                className="app-tile"
                onClick={() => {
                  navigate(`/${mod.name}`);
                  onClose();
                }}
              >
                <span
                  className="app-tile-icon"
                  style={{ backgroundColor: mod.color || "#714B67" }}
                  aria-hidden="true"
                >
                  <Icon />
                </span>
                <span className="app-tile-name">{mod.display_name}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
