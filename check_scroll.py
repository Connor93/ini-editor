import customtkinter as ctk

def check_structure():
    app = ctk.CTk()
    sf = ctk.CTkScrollableFrame(app)
    sf.pack()
    
    # Check for canvas
    if hasattr(sf, "_parent_canvas"):
        print("_parent_canvas found")
    else:
        print("_parent_canvas MISSING")
        
    app.update()
    app.destroy()

if __name__ == "__main__":
    check_structure()
