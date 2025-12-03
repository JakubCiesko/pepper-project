# Pepper Object Recognition with GPU-enabled Remote Machine
## 📝 Project Overview

This project implements a **dialog-based object recognition system** for the Pepper robot.
Pepper cannot run modern neural networks on-board, so the robot:

1. Captures an image using its camera
2. Sends the image over LAN to a **GPU-enabled computer**
3. A lightweight object detection model — such as **YOLOv8-nano** or **NanoDet** — processes the image
4. The detected objects are sent back to Pepper
5. Pepper generates a spoken, interactive response based on the recognition results

The system is designed for **low-latency inference**, **robust robot–server communication**, and **simple natural-language interaction**.

---

Run server-side in Google Colab with Free GPU: [https://colab.research.google.com/drive/1OBGuUm6ZNsYcBZLTqMpQPIfEJuwMMTJc?usp=sharing](https://colab.research.google.com/drive/1OBGuUm6ZNsYcBZLTqMpQPIfEJuwMMTJc?usp=sharing)

---
**Author: Jakub Ciesko**
