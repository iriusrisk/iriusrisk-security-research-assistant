import os
import subprocess
import sys
import time
import threading
import webbrowser
from pathlib import Path

import typer
from rich import print
from rich.progress import Progress, SpinnerColumn
from rich.progress import TextColumn, BarColumn, TimeRemainingColumn
from rich.style import Style

from isra.src.config.config import get_property
from isra.src.config.constants import ILE_JAR_FILE

app = typer.Typer(no_args_is_help=True, add_help_option=False)

# Global variables to track processes
backend_process = None
frontend_process = None


@app.callback()
def callback():
    """
    IriusRisk Library Editor
    """


def start_backend(port: int, app_dir: str):
    """Start the Python FastAPI backend server"""
    global backend_process
    
    # Check if uvicorn is available
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "--help"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[red]uvicorn is not installed. Installing dependencies...[/red]")
        print("[yellow]Please run: poetry install[/yellow]")
        return None
    
    # Set environment variables for the backend
    env = os.environ.copy()
    env['APPDIR'] = app_dir
    env['SERVER_PORT'] = str(port)
    env['SERVER_HOST'] = '127.0.0.1'
    
    # Get the backend directory
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        # Start the backend server
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "isra.src.ile.backend.main:app", 
            "--host", "127.0.0.1", 
            "--port", str(port),
            "--reload"
        ], cwd=Path(__file__).parent.parent.parent.parent, env=env)
        
        print(f"[green]Backend server started on http://127.0.0.1:{port}[/green]")
        return backend_process
        
    except Exception as e:
        print(f"[red]Error starting backend server: {e}[/red]")
        print("[yellow]Make sure all dependencies are installed with: poetry install[/yellow]")
        return None


def start_frontend(port: int):
    """Start the React frontend development server"""
    global frontend_process
    
    # Get the frontend directory
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Check if npm is available
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[red]npm is not installed or not in PATH. Please install Node.js and npm first.[/red]")
        print("[yellow]You can download Node.js from: https://nodejs.org/[/yellow]")
        return None
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("[yellow]Installing frontend dependencies...[/yellow]")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[red]Error installing frontend dependencies: {e}[/red]")
            return None
    
    try:
        # Set environment variables for the frontend
        env = os.environ.copy()
        env['PORT'] = str(port)
        env['REACT_APP_API_URL'] = f'http://127.0.0.1:{get_property("ile_port")}'
        
        # Start the frontend development server
        frontend_process = subprocess.Popen([
            "npm", "start"
        ], cwd=frontend_dir, env=env)
        
        print(f"[green]Frontend server started on http://127.0.0.1:{port}[/green]")
        return frontend_process
        
    except Exception as e:
        print(f"[red]Error starting frontend server: {e}[/red]")
        return None


def cleanup_processes():
    """Clean up running processes"""
    global backend_process, frontend_process
    
    if backend_process:
        try:
            backend_process.terminate()
            backend_process.wait(timeout=5)
        except:
            backend_process.kill()
        backend_process = None
    
    if frontend_process:
        try:
            frontend_process.terminate()
            frontend_process.wait(timeout=5)
        except:
            frontend_process.kill()
        frontend_process = None


@app.command()
def run():
    """
    Run an ILE instance (Python backend + React frontend)
    """
    # Validate configuration
    if get_property("ile_root_folder") == "":
        print("[red]No ILE root folder has been defined. Please configure 'ile_root_folder' in your settings.[/red]")
        raise typer.Exit(-1)
    
    if get_property("ile_port") == "":
        print("[red]No ILE port has been defined. Please configure 'ile_port' in your settings.[/red]")
        raise typer.Exit(-1)
    
    backend_port = int(get_property("ile_port"))
    frontend_port = backend_port + 1  # Frontend runs on next port
    
    with Progress(SpinnerColumn(),
                  TextColumn("[#01ECB4]Starting ILE...", justify="right"),
                  BarColumn(complete_style=Style(color="#01ECB4"), finished_style=Style(color="white")),
                  TimeRemainingColumn(),
                  ) as progress:
        task1 = progress.add_task("Description", total=2)
        print("[bold blue]IriusRisk Library Editor - Python Edition")
        print("1. This will launch the Python-based ILE backend and React frontend.")
        print("2. All elements will be stored where you have indicated in the ile_root_folder.")
        print("3. The backend API will run on the configured port.")
        print("4. The frontend will run on the next available port.")
        print("5. The application will be accessible in your web browser.")
        print(f"[green]Backend API: http://127.0.0.1:{backend_port}[/green]")
        print(f"[green]Frontend UI: http://127.0.0.1:{frontend_port}[/green]")

        while not progress.finished:
            progress.update(task1, advance=1)
            time.sleep(1)
    
    try:
        # Start backend server
        print("[blue]Starting backend server...[/blue]")
        backend_proc = start_backend(backend_port, get_property("ile_root_folder"))
        if not backend_proc:
            print("[red]Failed to start backend server[/red]")
            raise typer.Exit(-1)
        
        # Wait a moment for backend to start
        time.sleep(2)
        
        # Start frontend server
        print("[blue]Starting frontend server...[/blue]")
        frontend_proc = start_frontend(frontend_port)
        if not frontend_proc:
            print("[red]Failed to start frontend server[/red]")
            cleanup_processes()
            raise typer.Exit(-1)
        
        # Wait a moment for frontend to start
        time.sleep(3)
        
        # Open browser
        try:
            webbrowser.open(f"http://127.0.0.1:{frontend_port}")
        except:
            pass  # Browser opening is optional
        
        print(f"[bold green]ILE is now running![/bold green]")
        print(f"[green]Backend API: http://127.0.0.1:{backend_port}[/green]")
        print(f"[green]Frontend UI: http://127.0.0.1:{frontend_port}[/green]")
        print("[yellow]Press Ctrl+C to stop the servers[/yellow]")
        
        # Keep the main process alive and handle cleanup
        try:
            while True:
                time.sleep(1)
                # Check if processes are still running
                if backend_process and backend_process.poll() is not None:
                    print("[red]Backend server stopped unexpectedly[/red]")
                    break
                if frontend_process and frontend_process.poll() is not None:
                    print("[red]Frontend server stopped unexpectedly[/red]")
                    break
        except KeyboardInterrupt:
            print("\n[yellow]Shutting down ILE...[/yellow]")
        finally:
            cleanup_processes()
            print("[green]ILE stopped successfully[/green]")
            
    except Exception as e:
        print(f"[red]Error while launching ILE: {e}[/red]")
        cleanup_processes()
        raise typer.Exit(-1)


@app.command()
def backend():
    """
    Run only the ILE backend server
    """
    # Validate configuration
    if get_property("ile_root_folder") == "":
        print("[red]No ILE root folder has been defined. Please configure 'ile_root_folder' in your settings.[/red]")
        raise typer.Exit(-1)
    
    if get_property("ile_port") == "":
        print("[red]No ILE port has been defined. Please configure 'ile_port' in your settings.[/red]")
        raise typer.Exit(-1)
    
    backend_port = int(get_property("ile_port"))
    
    print("[bold blue]IriusRisk Library Editor - Backend Only")
    print("1. This will launch only the Python-based ILE backend.")
    print("2. All elements will be stored where you have indicated in the ile_root_folder.")
    print("3. The backend API will run on the configured port.")
    print(f"[green]Backend API: http://127.0.0.1:{backend_port}[/green]")
    
    try:
        # Start backend server
        print("[blue]Starting backend server...[/blue]")
        backend_proc = start_backend(backend_port, get_property("ile_root_folder"))
        if not backend_proc:
            print("[red]Failed to start backend server[/red]")
            raise typer.Exit(-1)
        
        print(f"[bold green]ILE Backend is now running![/bold green]")
        print(f"[green]Backend API: http://127.0.0.1:{backend_port}[/green]")
        print("[yellow]Press Ctrl+C to stop the server[/yellow]")
        
        # Keep the main process alive and handle cleanup
        try:
            while True:
                time.sleep(1)
                # Check if process is still running
                if backend_process and backend_process.poll() is not None:
                    print("[red]Backend server stopped unexpectedly[/red]")
                    break
        except KeyboardInterrupt:
            print("\n[yellow]Shutting down ILE Backend...[/yellow]")
        finally:
            cleanup_processes()
            print("[green]ILE Backend stopped successfully[/green]")
            
    except Exception as e:
        print(f"[red]Error while launching ILE Backend: {e}[/red]")
        cleanup_processes()
        raise typer.Exit(-1)


@app.command()
def frontend():
    """
    Run only the ILE frontend server
    """
    # Validate configuration
    if get_property("ile_port") == "":
        print("[red]No ILE port has been defined. Please configure 'ile_port' in your settings.[/red]")
        raise typer.Exit(-1)
    
    backend_port = int(get_property("ile_port"))
    frontend_port = backend_port + 1  # Frontend runs on next port
    
    print("[bold blue]IriusRisk Library Editor - Frontend Only")
    print("1. This will launch only the React frontend.")
    print("2. The frontend will run on the next available port.")
    print("3. Make sure the backend is running separately.")
    print(f"[green]Frontend UI: http://127.0.0.1:{frontend_port}[/green]")
    print(f"[yellow]Backend should be running on: http://127.0.0.1:{backend_port}[/yellow]")
    
    try:
        # Start frontend server
        print("[blue]Starting frontend server...[/blue]")
        frontend_proc = start_frontend(frontend_port)
        if not frontend_proc:
            print("[red]Failed to start frontend server[/red]")
            raise typer.Exit(-1)
        
        # Wait a moment for frontend to start
        time.sleep(3)
        
        # Open browser
        try:
            webbrowser.open(f"http://127.0.0.1:{frontend_port}")
        except:
            pass  # Browser opening is optional
        
        print(f"[bold green]ILE Frontend is now running![/bold green]")
        print(f"[green]Frontend UI: http://127.0.0.1:{frontend_port}[/green]")
        print("[yellow]Press Ctrl+C to stop the server[/yellow]")
        
        # Keep the main process alive and handle cleanup
        try:
            while True:
                time.sleep(1)
                # Check if process is still running
                if frontend_process and frontend_process.poll() is not None:
                    print("[red]Frontend server stopped unexpectedly[/red]")
                    break
        except KeyboardInterrupt:
            print("\n[yellow]Shutting down ILE Frontend...[/yellow]")
        finally:
            cleanup_processes()
            print("[green]ILE Frontend stopped successfully[/green]")
            
    except Exception as e:
        print(f"[red]Error while launching ILE Frontend: {e}[/red]")
        cleanup_processes()
        raise typer.Exit(-1)
