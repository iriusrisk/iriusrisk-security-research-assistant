import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

import typer
from rich import print

from isra.src.config.config import get_property

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


def start_frontend(port: int, backend_port: int):
    """Start the React frontend development server"""
    global frontend_process
    
    # Get the frontend directory
    frontend_dir = Path(__file__).parent.parent.parent.parent / "frontend"
    
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
        env['REACT_APP_API_URL'] = f'http://127.0.0.1:{backend_port}'
        
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
    Run the ILE application (backend API + frontend dev server)
    """
    # Validate configuration
    if get_property("ile_root_folder") == "":
        print("[red]No ILE root folder has been defined. Please configure 'ile_root_folder' in your settings.[/red]")
        raise typer.Exit(-1)
    
    if get_property("ile_port") == "":
        print("[red]No ILE port has been defined. Please configure 'ile_port' in your settings.[/red]")
        raise typer.Exit(-1)
    
    backend_port = int(get_property("ile_port"))
    frontend_port = backend_port + 1
    
    print("[bold blue]IriusRisk Library Editor")
    print("1. This will run the backend API and frontend development server on separate ports.")
    print("2. All elements will be stored where you have indicated in the ile_root_folder.")
    print("3. The application will be accessible in your web browser.")
    print(f"[green]Backend API: http://127.0.0.1:{backend_port}[/green]")
    print(f"[green]Frontend UI: http://127.0.0.1:{frontend_port}[/green]")
    
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
        frontend_proc = start_frontend(frontend_port, backend_port)
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