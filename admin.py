from flask import Flask, render_template, redirect, request, send_from_directory, url_for, session

def renderAdminstemplete():
    if 'user' in session:
        
        
        
        
        
        return render_template("admins.html")
    else:
        return redirect('/adminlogin')
    
    
    