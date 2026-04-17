import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  type KnowledgeArticle,
  type TicketCategory,
  createArticleApi,
  fetchArticleApi,
  fetchCategoriesApi,
  updateArticleApi,
} from "../../api/helpdesk";

interface FormState {
  title: string;
  slug: string;
  body: string;
  category: string;
  published: boolean;
}

const EMPTY_FORM: FormState = {
  title: "",
  slug: "",
  body: "",
  category: "",
  published: false,
};

export default function ArticleFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [categories, setCategories] = useState<TicketCategory[]>([]);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    fetchCategoriesApi()
      .then(setCategories)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!isEdit || !id) return;
    fetchArticleApi(Number(id))
      .then((a: KnowledgeArticle) => {
        setForm({
          title: a.title,
          slug: a.slug,
          body: a.body,
          category: a.category != null ? String(a.category) : "",
          published: a.published,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading article");
        setIsLoading(false);
      });
  }, [id, isEdit]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) => {
    const target = e.target as HTMLInputElement;
    const { name, value, type, checked } = target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const payload = {
      ...form,
      category: form.category ? Number(form.category) : null,
    };
    try {
      if (isEdit && id) {
        await updateArticleApi(Number(id), payload);
      } else {
        await createArticleApi(payload);
      }
      navigate("/helpdesk/articles");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>{headingPrefix} Article</h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="title">Title</label>
          <input
            id="title"
            name="title"
            value={form.title}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label htmlFor="slug">Slug</label>
          <input
            id="slug"
            name="slug"
            value={form.slug}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label htmlFor="category">Category</label>
          <select
            id="category"
            name="category"
            value={form.category}
            onChange={handleChange}
          >
            <option value="">-- None --</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="published">
            <input
              id="published"
              name="published"
              type="checkbox"
              checked={form.published}
              onChange={handleChange}
            />{" "}
            Published
          </label>
        </div>
        <div>
          <label htmlFor="body">Body (Markdown)</label>
          <textarea
            id="body"
            name="body"
            value={form.body}
            onChange={handleChange}
            rows={10}
          />
        </div>
        <button type="submit">Save</button>
      </form>
    </div>
  );
}
