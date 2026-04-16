import { NavLink } from "react-router-dom";
import { iconFor } from "./moduleIcons";

export interface SidebarItem {
  name: string;
  label: string;
  icon: string;
  url: string;
}

interface SidebarProps {
  items: SidebarItem[];
  isOpen: boolean;
}

export default function Sidebar({ items, isOpen }: SidebarProps) {
  if (!isOpen) return null;

  return (
    <aside className="sidebar" aria-label="Module navigation">
      <ul>
        {items.map((item) => {
          const Icon = iconFor(item.name);
          return (
            <li key={item.name}>
              <NavLink to={item.url} className="sidebar-link">
                <span className="sidebar-icon" aria-hidden="true">
                  <Icon />
                </span>
                <span className="sidebar-label">{item.label}</span>
              </NavLink>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
