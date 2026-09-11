### **Evaluation Metrics for Regression Models**

Regression models predict continuous values, and their performance is typically evaluated using various statistical error metrics. The most common metrics include **MSE, RMSE, MAE, MAPE, and R²**. Here’s a breakdown of each:

---

## **1. Mean Squared Error (MSE)**

**Definition:**  
MSE measures the average squared difference between actual values (yiy_i) and predicted values (y^i\hat{y}_i). It penalizes large errors more than small ones due to squaring.

MSE=1n∑i=1n(yi−y^i)2MSE = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2

✅ **Advantages:**

- Differentiable, making it useful for optimization (e.g., gradient descent).
    
- Heavily penalizes large errors.
    

❌ **Disadvantages:**

- Sensitive to outliers (due to squaring).
    

---

## **2. Root Mean Squared Error (RMSE)**

**Definition:**  
RMSE is the square root of MSE, which brings the error unit back to the original scale of the target variable.

RMSE=1n∑i=1n(yi−y^i)2RMSE = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2}

✅ **Advantages:**

- Same units as the target variable, making it easier to interpret.
    

❌ **Disadvantages:**

- Like MSE, it is sensitive to outliers.
    

---

## **3. Mean Absolute Error (MAE)**

**Definition:**  
MAE calculates the average absolute difference between actual and predicted values. Unlike MSE, it does not square the errors.

MAE=1n∑i=1n∣yi−y^i∣MAE = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|

✅ **Advantages:**

- Less sensitive to outliers compared to MSE.
    
- More interpretable since it represents the actual error magnitude.
    

❌ **Disadvantages:**

- Not differentiable at zero, which can make it less useful for certain optimization algorithms.
    

---

## **4. Mean Absolute Percentage Error (MAPE)**

**Definition:**  
MAPE expresses the error as a percentage of the actual values.

MAPE=1n∑i=1n∣yi−y^iyi∣×100MAPE = \frac{1}{n} \sum_{i=1}^{n} \left| \frac{y_i - \hat{y}_i}{y_i} \right| \times 100

✅ **Advantages:**

- Provides a relative measure of error (useful when working with different scales).
    

❌ **Disadvantages:**

- Cannot be used when actual values contain zero (division by zero issue).
    
- Puts more weight on small values than large values.
    

---

## **5. Coefficient of Determination (R2R^2)**

**Definition:**  
R2R^2 measures how well the regression model explains the variance in the actual data. It compares the model’s predictions to a simple mean-based model.

R2=1−∑(yi−y^i)2∑(yi−yˉ)2R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}

✅ **Advantages:**

- Ranges from 0 to 1 (higher is better).
    
- Measures how well the model fits the data.
    

❌ **Disadvantages:**

- Does not indicate how much error the model has in absolute terms.
    
- Can be misleading when used with non-linear models.
    

---

## **How to Compute MSE in R**

In R, you can calculate these metrics using built-in functions:

```r
# Sample data
actual <- c(3, -0.5, 2, 7)
predicted <- c(2.5, 0.0, 2, 8)

# Compute MSE
mse <- mean((actual - predicted)^2)
print(mse)
```

You can also use the `Metrics` package:

```r
install.packages("Metrics")
library(Metrics)

mse <- mse(actual, predicted)
mae <- mae(actual, predicted)
rmse <- rmse(actual, predicted)
r2 <- r2(actual, predicted)

print(mse)
print(mae)
print(rmse)
print(r2)
```

---

comparison table:

| Metric | Formula                                          | Interpretation                           | Sensitivity to Outliers |
| ------ | ------------------------------------------------ | ---------------------------------------- | ----------------------- |
| MSE    | 1n∑(yi−y^i)2\frac{1}{n} \sum (y_i - \hat{y}_i)^2 | Penalizes large errors more              | High                    |
| RMSE   | MSE\sqrt{MSE}                                    | Same unit as target, easier to interpret | High                    |
| MAE    | ( \frac{1}{n} \sum                               | y_i - \hat{y}_i                          | )                       |
| R2R^2  | 1−SSESST1 - \frac{SSE}{SST}                      | Explains model variance                  | Moderate                |
