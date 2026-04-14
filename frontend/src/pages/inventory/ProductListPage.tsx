import { useEffect, useState } from "react";
import { useTerminology } from "../../hooks/useTerminology";
import { type Product, fetchProductsApi } from "../../api/inventory";

export default function ProductListPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const productLabel = useTerminology("Product", "Product");

  useEffect(() => {
    fetchProductsApi()
      .then((data) => {
        setProducts(data);
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading products");
        setIsLoading(false);
      });
  }, []);

  return (
    <div>
      <h1>{productLabel}s</h1>

      {isLoading && <div>Loading...</div>}

      {error && <div>Error: {error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>SKU</th>
              <th>UOM</th>
              <th>Cost</th>
              <th>Sale Price</th>
              <th>Active</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.id}>
                <td>{product.name}</td>
                <td>{product.sku}</td>
                <td>{product.unit_of_measure}</td>
                <td>{product.cost_price}</td>
                <td>{product.sale_price}</td>
                <td>{product.is_active ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
