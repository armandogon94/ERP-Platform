import type { ComponentType, SVGProps } from "react";
import {
  Banknote,
  Building2,
  Calendar,
  ClipboardList,
  FileText,
  Headphones,
  LifeBuoy,
  Package,
  Receipt,
  ShoppingCart,
  Store,
  Truck,
  TrendingUp,
  Users,
  Wrench,
  type LucideIcon,
} from "lucide-react";

type Icon = LucideIcon | ComponentType<SVGProps<SVGSVGElement>>;

// Stable mapping from module key → Lucide icon.
// Covers all 13 ERP modules plus common aliases for Odoo-style names.
export const MODULE_ICONS: Record<string, Icon> = {
  accounting: Banknote,
  invoicing: Receipt,
  inventory: Package,
  hr: Users,
  sales: TrendingUp,
  purchasing: ShoppingCart,
  calendar: Calendar,
  calendar_module: Calendar,
  projects: ClipboardList,
  helpdesk: Headphones,
  support: LifeBuoy,
  fleet: Truck,
  manufacturing: Wrench,
  pos: Store,
  reports: FileText,
  partners: Building2,
  contacts: Building2,
};

/**
 * Resolve a module name to its Lucide icon component.
 * Returns `Package` as a neutral fallback when the module key is unknown.
 */
export function iconFor(moduleName: string): Icon {
  return MODULE_ICONS[moduleName] ?? Package;
}
