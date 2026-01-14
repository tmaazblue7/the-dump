from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import numpy as np

def validate_forecast(actual, predicted):
    """Compute MAPE and RMSE for forecast validation."""
    mape = mean_absolute_percentage_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    return {"MAPE": mape, "RMSE": rmse}
