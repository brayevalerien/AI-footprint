import streamlit as st
import pandas as pd
import plotly.express as px


if __name__ == "__main__":
    submited = False

    st.write("""
             # AI footprint
             ## Compute the CO2 footprint of your AI algorithm.
             """)

    device_types = ("CPU", "GPU", "Both")
    cpu_models = {
        "Core i3-10100": 0.0163,
        "AMD 7552": 0.0042,
        "Core i5-10500": 0.0108,
        "Core i9-10900XE": 0.0165,
        "Ryzen 5 1600": 0.0108,
        "Xeon Gold 6148": 0.0075
    }
    gpu_models = {
        "NVIDIA RTX 2080 Ti": 0.25,
        "AMD RX480": 0.15,
        "NVIDIA Tesla V100": 0.3,
        "NVIDIA Tesla P4": 0.075,
        "NVIDIA Tesla K80": 0.3,
    }
    cloud_providers = {
        "Azure": 1.125
    }
    server_regions = {
        "France": 51.28,
        "Ontario": 30,
        "California": 216.43,
        "Kentucky": 804.75,
        "Austria": 111.18,
        "Taiwan": 509
    }

    with st.sidebar.form("parameters"):
        st.write("# Model & training parameters")
        st.write("----")

        st.write("# Data")
        data_size = st.number_input(
            "Amount of training data stored (GB)", min_value=0)
        storage_time = st.number_input(
            "Data storage time (hours)", min_value=0)

        st.write("# Training")
        training_time = st.number_input(
            "Training duration (hours)", min_value=0)
        training_device_type = st.selectbox(
            "Training device type", device_types)
        training_cpu_cores = st.slider(
            "Training number of CPU cores", 1, 32, 8)
        training_cpu_model = st.selectbox("Training CPU model", cpu_models)
        training_gpu = st.slider("Training number of GPUs", 1, 16, 8)
        training_gpu_model = st.selectbox("Training GPU model", gpu_models)
        training_ram = st.slider("Training RAM (GB)", 1, 64, 16)

        st.write("# Inference")
        inference_time = st.number_input(
            "Inference duration (hours)", min_value=0)
        inference_device_type = st.selectbox(
            "Inference device type", device_types)
        inference_cpu_cores = st.slider(
            "Inference number of CPU cores", 1, 32, 8)
        inference_cpu_model = st.selectbox("Inference CPU model", cpu_models)
        inference_gpu = st.slider("Inference number of GPUs", 1, 16, 8)
        inference_gpu_model = st.selectbox("Inference GPU model", gpu_models)
        inference_ram = st.slider("Inference RAM (GB)", 1, 64, 16)

        st.write("# Cloud computing")
        cloud_provider = st.selectbox("Cloud provider", cloud_providers.keys())
        server_region = st.selectbox("Server region", server_regions)

        submited = st.form_submit_button("Submit")

    if submited:
        datacenter_efficiency = cloud_providers[cloud_provider]
        datacenter_emission = server_regions[server_region]
        training_cpu_power = cpu_models[training_cpu_model]
        training_gpu_power = gpu_models[training_gpu_model]
        inference_cpu_power = cpu_models[inference_cpu_model]
        inference_gpu_power = gpu_models[inference_gpu_model]
        power_per_gb_stored = 0.000001
        power_per_ram_gb = 0.0003725

        cloud_efficiency = datacenter_efficiency*datacenter_emission/1000
        total_training = training_cpu_cores * \
            training_cpu_power if training_device_type in (
                "CPU", "Both") else 0
        total_training += training_gpu * \
            training_gpu_power if training_device_type in (
                "GPU", "Both") else 0
        total_training += training_ram*power_per_ram_gb
        total_training *= training_time * cloud_efficiency
        total_inference = inference_cpu_cores * \
            inference_cpu_power if inference_device_type in (
                "CPU", "Both") else 0
        total_inference += inference_gpu * \
            inference_gpu_power if inference_device_type in (
                "GPU", "Both") else 0
        total_inference += inference_ram*power_per_ram_gb
        total_inference *= inference_time * cloud_efficiency
        total_storage = storage_time*power_per_gb_stored * cloud_efficiency
        total = (total_inference + total_training + total_storage)

        st.write(f"""
                 Data has been submited successfully.
                 ### Carbon footprint (kg of CO$_2$ equivalent):
                 | Data storage        | Model training       | Model inference       | 
                 | :-----------------: | :------------------: | :-------------------: | 
                 | {total_storage:.5g} | {total_training:.5g} | {total_inference:.5g} | 
                 """)

        # Plot pie chart
        pie_chart_data = {
            'Activity': ['Storage', 'Inference', 'Training'],
            'Emissions': [total_storage, total_inference, total_training]
        }
        pie_chart_df = pd.DataFrame(pie_chart_data)
        # Colors used for each activity
        colors = ['#66d9ef', '#f92672', '#e2e22e']
        fig = px.pie(pie_chart_df, values='Emissions', names='Activity',
                     title='Emissions per activity', color_discrete_sequence=colors)
        st.plotly_chart(fig, use_container_width=True)

        st.write(f"""
                 #### Total: {total:.5g}
                 
                 ### Equivalents
                 Compare your system to real world activities.
                 | Activities with high carbon emissions | Your emissions compared to these activities |
                 |---|---|
                 | Evry - Palaiseau trip (bus, one-way, 1 passenger) | {total/0.10265936644505277:.5e} |
                 | Production of an average smartphone               | {total/16.39:.5e}              |
                 | Paris - Marseille trip (car, one-way)             | {total/151.34923738756353:.5e} |
                 | Paris - New-York flight (round trip, 1 passenger) | {total/1984e3:.5e}             |
                 | 1 human life (average)                            | {total/11023e3:.5e}            |
                 | 1 human life (as an american)                     | {total/36156e3:.5e}            |
                 | Buying and using a car (including oil)            | {total/126e6:.5e}              |
                 """)
    else:
        st.write("Fill the form in the side bar to get an estimation of your CO2 emissions. If the precise answer is not available, choose the closes option.")
