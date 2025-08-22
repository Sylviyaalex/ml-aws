# import numpy as np
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
from pathlib import Path

# Create tiny dummy data (y = 2*x1 + 3*x2 + noise)
rng = np.random.default_rng(42)
X = rng.normal(size=(200, 2))
y = 2*X[:, 0] + 3*X[:, 1] + rng.normal(scale=0.1, size=200)

model = LinearRegression()
model.fit(X, y)

# Save as joblib
out_path = Path(__file__).parent / "model.joblib"
joblib.dump(model, out_path)
print(f"Saved model to {out_path.resolve()}")
