# -*- coding: utf-8 -*-
"""app.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-v3SIXtwpl4sH_M4O6IOgSo4SVKL5yty
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam, SGD, RMSprop
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Streamlit UI
st.title('📊 Sales Prediction Dashboard - ANN')

# Upload dataset
uploaded_train = st.file_uploader("📂 Upload Train CSV", type=['csv'])
uploaded_store = st.file_uploader("📂 Upload Store CSV", type=['csv'])

if uploaded_train and uploaded_store:
    # Load datasets
    train_df = pd.read_csv(uploaded_train)
    store_df = pd.read_csv(uploaded_store)

    st.write("### 🔍 Train Dataset Preview:", train_df.head())
    st.write("### 🔍 Store Dataset Preview:", store_df.head())

    # 🔥 Merge the datasets on Store ID
    df = train_df.merge(store_df, how="left", on="Store")

    # ✅ Drop unnecessary columns
    columns_to_drop = ['Customers', 'PromoInterval']  # 'Customers' is not needed for predictions
    df.drop(columns=columns_to_drop, inplace=True)

    # ✅ Convert date column to datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # ✅ Extract date features
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week

    # ✅ Handle missing values
    df['CompetitionDistance'].fillna(df['CompetitionDistance'].median(), inplace=True)
    df['CompetitionOpenSinceMonth'].fillna(0, inplace=True)
    df['CompetitionOpenSinceYear'].fillna(0, inplace=True)
    df['Promo2SinceWeek'].fillna(0, inplace=True)
    df['Promo2SinceYear'].fillna(0, inplace=True)

    # ✅ Encoding categorical variables
    cat_cols = ['StoreType', 'Assortment', 'StateHoliday']
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)

    # ✅ Scaling numerical features
    num_cols = ['CompetitionDistance', 'CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear',
                'Promo2SinceWeek', 'Promo2SinceYear', 'Year', 'Month', 'Day', 'WeekOfYear']

    scaler = StandardScaler()
    df[num_cols] = scaler.fit_transform(df[num_cols])

    # ✅ Train-Test Split
    X = df.drop(columns=['Sales', 'Date'])
    y = df['Sales']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    st.write("✅ Data Preprocessing Complete!")

    # Sidebar for Hyperparameter Selection
    st.sidebar.header("Model Hyperparameters")

    num_layers = st.sidebar.slider("Number of Hidden Layers", 1, 5, 3)
    neurons_per_layer = st.sidebar.slider("Neurons per Layer", 32, 256, 128)
    activation = st.sidebar.selectbox("Activation Function", ['relu', 'tanh', 'sigmoid'])
    dropout_rate = st.sidebar.slider("Dropout Rate", 0.0, 0.5, 0.3)
    optimizer = st.sidebar.selectbox("Optimizer", ['adam', 'sgd', 'rmsprop'])
    learning_rate = st.sidebar.slider("Learning Rate", 0.0001, 0.01, 0.001)
    epochs = st.sidebar.slider("Number of Epochs", 10, 100, 50)

    # Model Training Button
    if st.button("🚀 Train Model"):
        with st.spinner('Training ANN Model... Please wait!'):

            # Build ANN Model
            model = Sequential()

            # Input Layer
            model.add(Dense(neurons_per_layer, activation=activation, input_shape=(X_train.shape[1],)))
            model.add(BatchNormalization())
            model.add(Dropout(dropout_rate))

            # Hidden Layers
            for _ in range(num_layers - 1):
                model.add(Dense(neurons_per_layer, activation=activation))
                model.add(BatchNormalization())
                model.add(Dropout(dropout_rate))

            # Output Layer
            model.add(Dense(1, activation='linear'))

            # Compile Model
            optimizer_dict = {
                "adam": Adam(learning_rate=learning_rate),
                "sgd": SGD(learning_rate=learning_rate),
                "rmsprop": RMSprop(learning_rate=learning_rate)
            }

            model.compile(
                loss='mse',
                optimizer=optimizer_dict[optimizer],
                metrics=['mae']
            )

            # Train the model
            history = model.fit(
                X_train, y_train,
                validation_data=(X_test, y_test),
                epochs=epochs,
                batch_size=64,
                verbose=1
            )

            st.success("🎉 Model Training Completed!")

            # Plot Loss
            fig, ax = plt.subplots()
            ax.plot(history.history['loss'], label='Training Loss')
            ax.plot(history.history['val_loss'], label='Validation Loss')
            ax.set_xlabel("Epochs")
            ax.set_ylabel("Loss")
            ax.legend()
            st.pyplot(fig)

            # Plot MAE
            fig, ax = plt.subplots()
            ax.plot(history.history['mae'], label='Training MAE')
            ax.plot(history.history['val_mae'], label='Validation MAE')
            ax.set_xlabel("Epochs")
            ax.set_ylabel("MAE")
            ax.legend()
            st.pyplot(fig)

            # 📈 Plot Actual vs Predicted Sales
            y_pred = model.predict(X_test)
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.scatter(y_test, y_pred, alpha=0.5, label='Predicted vs Actual', color='royalblue')
            ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', label='Perfect Prediction')
            ax.set_xlabel('Actual Sales')
            ax.set_ylabel('Predicted Sales')
            ax.set_title('📊 Actual vs Predicted Sales')
            ax.legend()
            st.pyplot(fig)

            # 📉 Residual Plot - difference between the actual and predicted sales
            residuals = y_test - y_pred.flatten()
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.scatter(y_pred, residuals, alpha=0.5, color='purple')
            ax.axhline(0, color='red', linestyle='--')
            ax.set_xlabel('Predicted Sales')
            ax.set_ylabel('Residuals')
            ax.set_title('📉 Residual Plot')
            st.pyplot(fig)

            # 🎯 Sales Distribution Plot : How scaling impacts the data distribution
            fig, ax = plt.subplots(1, 2, figsize=(14, 6))

            # Before Scaling
            ax[0].hist(train_df['Sales'], bins=50, color='lightblue', alpha=0.7)
            ax[0].set_title('📊 Sales Distribution (Before Scaling)')
            ax[0].set_xlabel('Sales')
            ax[0].set_ylabel('Frequency')

            # After Scaling
            ax[1].hist(y_train, bins=50, color='lightgreen', alpha=0.7)
            ax[1].set_title('📈 Sales Distribution (After Scaling)')
            ax[1].set_xlabel('Scaled Sales')
            ax[1].set_ylabel('Frequency')

            st.pyplot(fig)

            # Final Evaluation
            y_pred = model.predict(X_test)

            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            st.write("### ✅ Model Evaluation")
            st.write(f"📈 MSE: {mse:.4f}")
            st.write(f"📉 MAE: {mae:.4f}")
            st.write(f"🔢 R² Score: {r2:.4f}")

            # Model Summary
            st.write("### 🔥 Model Summary")

            for layer in model.layers:
              output_shape = layer.get_output_shape_at(0) if hasattr(layer, 'get_output_shape_at') else "N/A" # Use get_output_shape_at() for better compatibility
              st.write(f"Layer: {layer.name}, Output Shape: {output_shape}, Parameters: {layer.count_params()}")
