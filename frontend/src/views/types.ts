/** Field type in a view configuration */
export type FieldType =
  | "char"
  | "text"
  | "integer"
  | "float"
  | "decimal"
  | "date"
  | "datetime"
  | "boolean"
  | "selection"
  | "many2one"
  | "one2many"
  | "many2many";

/** Column definition for ListView */
export interface ListColumn {
  field: string;
  label: string;
  type?: FieldType;
  sortable?: boolean;
  width?: string;
}

/** Field definition for FormView */
export interface FormField {
  field: string;
  label: string;
  type: FieldType;
  required?: boolean;
  readonly?: boolean;
  placeholder?: string;
  relation?: string;
  options?: { value: string; label: string }[];
}

/** Section grouping fields in FormView */
export interface FormSection {
  title: string;
  fields: FormField[];
}

/** Kanban column definition */
export interface KanbanColumn {
  value: string;
  label: string;
  color?: string;
}

/** List view configuration */
export interface ListViewConfig {
  columns: ListColumn[];
  default_order?: string;
  search_fields?: string[];
}

/** Form view configuration */
export interface FormViewConfig {
  sections: FormSection[];
}

/** Kanban view configuration */
export interface KanbanViewConfig {
  column_field: string;
  columns: KanbanColumn[];
  card_fields: string[];
}

/** Generic record type */
export type Record = {
  id: number;
  [key: string]: unknown;
};
