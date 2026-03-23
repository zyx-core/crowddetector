# Crowd Counting Mobile App

This folder contains the Flutter project for the offline mobile app.

## Prerequisites

1.  **Flutter SDK**: [Install Flutter](https://docs.flutter.dev/get-started/install)
2.  **Android Studio** (for Android) or **Xcode** (for iOS/Mac).

## Setup Instructions

1.  **Navigate to the app folder**:
    ```bash
    cd mobile_app
    ```

2.  **Initialize the project**:
    Since this was generated automatically, you need to creating the build files:
    ```bash
    flutter create .
    ```

3.  **Install dependencies**:
    ```bash
    flutter pub get
    ```

4.  **Copy Model File**:
    Ensure the `best_int8.tflite` (or `best_float32.tflite`) file is in the `assets` folder.
    *Note: The conversion script in the root folder (`convert_to_tflite.py`) generates this file.*

5.  **Android Configuration (Important)**:
    Open `android/app/build.gradle` and ensure:
    ```gradle
    defaultConfig {
        ...
        minSdkVersion 21  // Must be at least 21 for camera/tflite
        ...
    }
    ```

## Running the App

1.  Connect your phone via USB (enable Developer Mode & USB Debugging).
2.  Run the app:
    ```bash
    flutter run --release
    ```

## Troubleshooting

-   **Model not found**: Check `pubspec.yaml` assets section matches the filename in `assets/`.
-   **Camera permission**: The app should ask for permission on first run. If not, check app settings.
