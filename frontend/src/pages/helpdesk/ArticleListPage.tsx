import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { type KnowledgeArticle, fetchArticlesApi } from "../../api/helpdesk";
import Skeleton from "../../components/Skeleton";

export default function ArticleListPage() {
  const [rows, setRows] = useState<KnowledgeArticle[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchArticlesApi()
      .then(setRows)
      .catch((err: Error) => setError(err.message || "Error loading articles"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>Knowledge Base</h1>

      <Link to="/helpdesk/articles/new">New Article</Link>

      {isLoading && <Skeleton />}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Slug</th>
              <th>Category</th>
              <th>Published</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((a) => (
              <tr key={a.id}>
                <td>
                  <Link to={`/helpdesk/articles/${a.id}/edit`}>{a.title}</Link>
                </td>
                <td>{a.slug}</td>
                <td>{a.category_name ?? "—"}</td>
                <td>{a.published ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
