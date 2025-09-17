import time
import streamlit as st
import random
from typing import Dict
import argparse

from src.config_loader import ConfigLoader
from src.os import OperatingSystem

def get_cli_args():
    parser = argparse.ArgumentParser(description="Эмулятор Операционной Системы")
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Начальное значение для генератора случайных чисел (RNG seed)'
    )
    try:
        args, unknown = parser.parse_known_args()
    except SystemExit:
        args = parser.parse_args([])

    return args

cli_args = get_cli_args()

def get_system_config(loader: ConfigLoader) -> Dict:
    config = loader.get_system_config()
    if not config:
        return {
            "memory": 1024,
            "max_processes": 10,
            "quantum_length": 5,
            "io_duration": 15,
            "initial_speed_hz": 1.0,
        }
    return config

def initialize_os(seed: int):
    random.seed(seed)
    st.session_state.seed = seed

    config_loader = ConfigLoader(filepath="parameters.json")
    system_config = get_system_config(config_loader)

    os_instance = OperatingSystem(
        system_config=system_config,
        config_loader=config_loader
    )
    os_instance.boot()
    return os_instance

def display_stats(stats_data):
    st.header("Панель мониторинга ОС")

    col1, col2, col3 = st.columns(3)
    col1.metric("Системное время (такты)", stats_data['system_tick'])
    col2.metric("Скорость (такты/сек)", f"{stats_data['speed_hz']:.1f}")
    col3.metric("Память", stats_data['memory_usage'])

    st.subheader("Процессы")
    col1, col2, col3 = st.columns(3)
    col1.metric("Всего процессов", stats_data['process_count'])
    col2.metric("Готовых", stats_data['ready_count'])
    col3.metric("Заблокированных", stats_data['blocked_count'])

    st.subheader("CPU и Задания")
    col1, col2, col3 = st.columns(3)
    col1.metric("Состояние CPU", stats_data['cpu_state'])
    col2.metric("Активный PID", stats_data['active_pid'])

    next_task_str = "Нет"
    if stats_data['next_task']:
        next_task_str = f"P(size={stats_data['next_task'].size}, len={stats_data['next_task'].program_length})"
    col3.metric("Следующее задание", next_task_str)

    st.subheader("Таблица процессов (PSW)")
    if stats_data['all_processes']:
        proc_list = [p.__dict__ for p in stats_data['all_processes']]
        st.dataframe(proc_list, use_container_width=True)
    else:
        st.info("В системе нет процессов.")

    st.subheader("История выполнения на CPU")
    history_str = ' -> '.join(map(str, stats_data['execution_history']))
    st.text(history_str if history_str else "История пуста.")


st.set_page_config(layout="wide", page_title="Эмулятор ОС")

if 'os_instance' not in st.session_state:
    st.session_state.os_instance = initialize_os(seed=cli_args.seed)
    st.session_state.is_running = False

os_emulator = st.session_state.os_instance

with st.sidebar:
    st.title("Админ панель")

    current_seed = st.session_state.get('seed', 'N/A')
    st.caption(f"RNG Seed: `{current_seed}`")

    st.divider()

    st.header("Управление симуляцией")

    tick_button_pressed = st.button("Выполнить 1 тик")

    if st.session_state.get('is_running', False):
        if st.button("Пауза", type="primary"):
            st.session_state.is_running = False
            st.rerun()
    else:
        if st.button("Старт"):
            st.session_state.is_running = True
            st.rerun()

    new_speed = st.slider(
        "Скорость (такты/сек)",
        min_value=0.1,
        max_value=100.0,
        value=os_emulator.speed_hz,
        step=0.5,
        format="%.1f такт/сек"
    )

    if new_speed != os_emulator.speed_hz:
        os_emulator.set_speed(new_speed)
        st.rerun()

    st.divider()

    st.header("Управление заданиями")

    auto_load_checkbox = st.checkbox(
        "Автоматическая загрузка заданий",
        value=os_emulator.auto_load_enabled
    )
    if auto_load_checkbox != os_emulator.auto_load_enabled:
        os_emulator.toggle_auto_load(auto_load_checkbox)
        st.rerun()

    if st.button("Загрузить новое задание вручную"):
        result = os_emulator.force_load_next_task()
        if "Ошибка" in result:
            st.toast(result)
        else:
            st.toast(result)
        st.rerun()

    with st.expander("Задать параметры для следующего задания"):
        p_size = st.number_input("Размер процесса", min_value=16, max_value=512, value=128, step=16)
        p_len = st.number_input("Длина программы", min_value=10, max_value=100, value=30, step=5)
        p_io = st.slider("Вероятность I/O", min_value=0.0, max_value=1.0, value=0.2, step=0.05)

        if st.button("Применить параметры"):
            params = {"process_size": p_size, "program_length": p_len, "io_command_probability": p_io}
            os_emulator.set_custom_task_params(params)
            st.toast("Параметры для следующего задания установлены!")
            st.rerun()

    st.divider()

    st.header("Управление процессами")

    all_pids = os_emulator.process_manager.get_all_pids()
    pids_str = ", ".join(map(str, all_pids))
    st.caption(f"Доступные PID: {pids_str}" if pids_str else "Нет активных процессов")

    pid_input = st.number_input("Введите PID процесса:", min_value=0, step=1)

    col1, col2, col3 = st.columns(3)

    def handle_process_action(action_func, pid: int):
        if not os_emulator.process_manager.get_process(pid):
            st.error(f"Процесса с PID {pid} не существует в системе.")
            time.sleep(2)
            st.rerun()
            return
        result = action_func(pid)
        if "Ошибка" in result:
            st.warning(result)
        else:
            st.success(result)
        time.sleep(1.5)
        st.rerun()

    with col1:
        if st.button("Приостановить"):
            handle_process_action(os_emulator.suspend_process, pid_input)
    with col2:
        if st.button("Возобновить"):
             handle_process_action(os_emulator.resume_process, pid_input)
    with col3:
        if st.button("Уничтожить"):
             handle_process_action(os_emulator.kill_process, pid_input)

    st.divider()

    st.header("Системные настройки")

    mem_size = st.number_input(f"Размер памяти (текущий: {os_emulator.memory_manager.total_size})", min_value=64, step=64, value=os_emulator.memory_manager.total_size)
    if st.button("Изменить память"):
        result = os_emulator.resize_memory(mem_size)
        if "Ошибка" in result:
            st.error(result)
        else:
            st.success(result)
        time.sleep(2)
        st.rerun()

    if st.button("Выполнить задания и выключить", type="secondary"):
        st.session_state.is_running = True
        os_emulator.initiate_graceful_shutdown()
        st.warning("Режим штатного выключения активирован.")
        time.sleep(2.5)
        st.rerun()


if not os_emulator._running:
    st.success("Симуляция завершена.")
    st.stop()

if tick_button_pressed:
    os_emulator.execute_tick()
    st.rerun()

all_stats = os_emulator.get_system_stats()
display_stats(all_stats)

if st.session_state.get('is_running', False):
    sleep_duration = 1.0 / os_emulator.speed_hz if os_emulator.speed_hz > 0 else 1
    time.sleep(sleep_duration)
    os_emulator.execute_tick()
    st.rerun()
