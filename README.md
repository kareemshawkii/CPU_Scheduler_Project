# **CPU Scheduling Algorithm Simulator**

A desktop-based CPU Scheduler application built with Python that simulates and visualizes various CPU scheduling algorithms. The application provides a user-friendly graphical interface to analyze process scheduling in both real-time (live) and static (pre-loaded) execution modes.

This project aims to provide a practical tool for students, educators, and enthusiasts to understand and compare the behavior and performance of different scheduling policies in an operating system.

## **📸 Screenshots**

A screenshot showing the main interface with processes and algorithm selection.

A screenshot of the Gantt chart visualization after a simulation.

## **✨ Key Features**

* **GUI-Based Simulation:** An intuitive graphical user interface to manage processes and simulations.  
* **Multiple Scheduling Algorithms:** Implementation of a wide range of common CPU scheduling algorithms.  
* **Two Execution Modes:**  
  * **Static Mode:** Load a predefined set of processes and run the simulation.  
  * **Real-Time (Live) Mode:** Add processes dynamically while the simulation is running.  
* **Gantt Chart Visualization:** Clear and detailed Gantt charts to visualize the scheduling timeline.  
* **Performance Metrics:** Calculation and display of key performance metrics, such as:  
  * Average Waiting Time  
  * Average Turnaround Time  
  * CPU Utilization  
* **Process Management:** Easily add, edit, and remove processes with properties like Arrival Time, Burst Time, and Priority.  
* **Configurable Settings:** Adjust simulation speed and other parameters for better analysis.

## **⚙️ Supported Algorithms**

The simulator currently supports the following scheduling algorithms:

* **First-Come, First-Served (FCFS)**  
* **Shortest Job First (SJF)**  
  * Non-Preemptive  
  * Preemptive (Shortest Remaining Time First \- SRTF)  
* **Priority Scheduling**  
  * Non-Preemptive  
  * Preemptive  
* **Round Robin (RR)**

## **🚀 Getting Started**

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### **Prerequisites**

You will need the following software installed on your system:

* **Python** \- Version 3.8 or higher  
* **pip** (Python package installer)  
* An IDE like **VS Code**, **PyCharm**, or **Sublime Text** is recommended.

### **Installation & Running the Application**

1. **Clone the repository:**  
   git clone https://github.com/kareemshawkii/CPU\_Scheduler\_Project  
   cd your-repository-name

2. **(Recommended) Create and activate a virtual environment:**  
   * On Windows:  
     python \-m venv venv  
     .\\venv\\Scripts\\activate

   * On macOS/Linux:  
     python3 \-m venv venv  
     source venv/bin/activate

3. **Install the required dependencies:**  
   pip install \-r requirements.txt

4. **Run the application:**  
   python main.py

   *(Note: The entry point script might be named differently, e.g., app.py)*

## **📖 How to Use**

1. **Launch the application** using the command from the installation steps.  
2. **Select a Scheduling Algorithm** from the dropdown menu.  
3. **Configure Parameters:**  
   * For algorithms like Round Robin, set the **Time Quantum**.  
   * For real-time mode, you can set the simulation speed.  
4. **Add Processes:**  
   * Use the "Add Process" form to input the **Process ID**, **Arrival Time**, **Burst Time**, and **Priority** (if applicable).  
   * Click the "Add" button to add the process to the queue.  
5. **Choose an Execution Mode:**  
   * **Static Mode:** After adding all desired processes, click the **"Run Simulation"** button.  
   * **Live Mode:** Click the **"Start Live Simulation"** button. You can continue to add processes even after the simulation has started.  
6. **Analyze Results:**  
   * Observe the **Gantt Chart** as it is being generated.  
   * Review the final **Performance Metrics Table** for a summary of waiting and turnaround times.  
   * Click **"Reset"** to clear the current simulation and start a new one.

## **🛠️ Technology Stack**

* **Language:** Python  
* **UI Toolkit:** Tkinter / PyQt5 / CustomTkinter  
* **Key Libraries:**  
  * (e.g., matplotlib for plotting the Gantt chart)  
  * (e.g., pandas for data handling)

## **🤝 Contributing**

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. **Fork the Project**  
2. **Create your Feature Branch** (git checkout \-b feature/AmazingFeature)  
3. **Commit your Changes** (git commit \-m 'Add some AmazingFeature')  
4. **Push to the Branch** (git push origin feature/AmazingFeature)  
5. **Open a Pull Request**

Please make sure to update tests as appropriate.

## 