from django.shortcuts import render, redirect
from django.http import JsonResponse
from pathlib import Path
import base64
import os
import json
import shutil
import random

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = "DataStorage"

def get_fav_icon():
    with open(f"{BASE_DIR}//favicon.png", "rb") as fi:
        icon_data = fi.read()
        b64_icon_data = base64.b64encode(icon_data)
        base64_icon_data = b64_icon_data.decode("UTF-8")
    return base64_icon_data

public_notes_html = """
<div id="new_elem">
    <div class="title_div">
        <p class="n_title">{}</p>
        <p class="n_title">Written by: {}</p>
    </div>
    <div class="body_div">
        {}
    </div>
</div>
"""

def get_public_notes():
    public_notes_path = f"{BASE_DIR}//public"
    public_notes_list = os.listdir(public_notes_path)
    public_notes_list.remove("blank")
    if public_notes_list:
        all_public_notes = []
        for uname in public_notes_list:
            one_user_public_notes_list = os.listdir(f"{public_notes_path}//{uname}")
            if one_user_public_notes_list:
                for public_notes in one_user_public_notes_list:
                    one_public_note = []
                    one_public_note.append(uname)
                    one_public_note.append(public_notes)
                    with open(f"{public_notes_path}//{uname}//{public_notes}//note.n", "rb") as pn:
                        act_public_note = pn.read()
                        one_public_note.append(act_public_note.decode())
                    all_public_notes.append(one_public_note)
        all_public_notes_html_list = []
        for pn in all_public_notes:
            final_html_list = public_notes_html.format(pn[1], pn[0], pn[2])
            all_public_notes_html_list.append(final_html_list)
        random.shuffle(all_public_notes_html_list)
        return "".join(all_public_notes_html_list)
    else:
        return ""

def render_home_page(request):
    home_page_data = {
        "favicon": get_fav_icon(),
        "publicnotes": get_public_notes()
    }
    return render(request, "home.html", home_page_data)

def render_login_page(request):
    return render(request, "login.html", {"favicon": get_fav_icon()})

def get_registered_user_data(user):
    try:
        with open(f"{BASE_DIR}//{DB_PATH}//{user}//account.json", "r") as ud:
            user_data = ud.read()
            return user_data
    except Exception as e:
        print(e)
        return None

NOTE_HTML = """
<div id="new_elem">
    <div class="title_div">
        <p class="n_title" id="{}">{}</p>
        <p class="n_title" id="{}">Note is {}</p>
        <div>
            <button class="d_btn" onclick="delete_note()" id="{}">Delete</button>
            <button class="e_btn" onclick="edit_note()" id="{}">Edit</button>
        </div>
    </div>
    <div class="body_div">
    {}
    </div>
</div>
"""

def get_all_notes(user):
    all_notes_path = f"{BASE_DIR}//{DB_PATH}//{user}"
    all_notes_list = os.listdir(all_notes_path)
    all_notes_list.remove("account.json")
    all_notes_list.reverse()
    all_notes_data_list = []
    if all_notes_list:
        for index, data in enumerate(all_notes_list):
            one_note = []
            one_note.append(str(index))
            one_note.append(data)
            with open(f"{all_notes_path}//{data}//note.json", "r") as nte:
                note_data = json.loads(nte.read())
                one_note.append(note_data["pp"])
                one_note.append(note_data["note"])
            all_notes_data_list.append(one_note)
        all_html_elements = []
        for one_note in all_notes_data_list:
            final_html = NOTE_HTML.format(
                f"{one_note[0]}{one_note[0]}",
                f"{one_note[1]}",
                f"{one_note[0]}{one_note[0]}{one_note[0]}",
                f"{one_note[2]}",
                f"{one_note[0]}",
                f"{one_note[0]}",
                f"{one_note[3]}"
            )
            all_html_elements.append(final_html)
        return "".join(all_html_elements)
    else:
        return ""

def delete_notes(request):
    uname = request.POST["username"]
    psw = request.POST["password"]
    porp = request.POST["porp"]
    key2del = request.POST["key2del"]
    new_porp = str(porp).split()
    p_or_p = new_porp[-1].lower()
    private_delete_path = f"{BASE_DIR}//{DB_PATH}//{uname}//{key2del}"
    public_delete_path = f"{BASE_DIR}//public//{uname}//{key2del}"
    all_delete_paths = [private_delete_path, public_delete_path]
    if json.loads(get_registered_user_data(uname))["password"] == psw:
        if p_or_p == "private":
            shutil.rmtree(all_delete_paths[0])
        else:
            for pth in all_delete_paths:
                shutil.rmtree(pth)
        return JsonResponse({"status": "deleted"}, safe=False)
    else:
        return JsonResponse({"status": "error"}, safe=False)

def check_login(request):
    username = request.POST["username"]
    password = request.POST["password"]
    if check_user_existence(username):
        if get_registered_user_data(username) != None:
            user_data = json.loads(get_registered_user_data(username))
            if password == user_data["password"]:
                login_success = {
                    "status": "login_success",
                    "uname": username,
                    "passw": password,
                    "allnotes": get_all_notes(username),
                }
                return JsonResponse(login_success, safe=False)
            else:
                return JsonResponse({"status": "incorrect_password"}, safe=False)
        else:
            return JsonResponse({"status": "error_occured"}, safe=False)
    else:
        return JsonResponse({"status": "no_user"}, safe=False)

def edit_account_json(*args):
    uname, mode, data = args
    with open(f"{BASE_DIR}//{DB_PATH}//{uname}//account.json", mode) as acc:
        if mode == "r":
            return acc.read()
        elif mode == "w":
            acc.write(data)

def reset_password(request, uname):
    if uname == "finishresetp":
        new_uname = request.POST["uname"]
        ans1 = request.POST["ans1"]
        ans2 = request.POST["ans2"]
        passw = request.POST["passw"]
        status_data = "none"
        saved_answer1 = json.loads(
            get_registered_user_data(new_uname))["answer1"]
        saved_answer2 = json.loads(
            get_registered_user_data(new_uname))["answer2"]
        if saved_answer1 == ans1 and saved_answer2 == ans2:
            u_d = json.loads(edit_account_json(new_uname, "r", ""))
            _, q1, a1, q2, a2 = u_d["password"], u_d["question1"], u_d["answer1"], u_d["question2"], u_d["answer2"]
            new_data = {
                "password": passw,
                "question1": q1,
                "answer1": a1,
                "question2": q2,
                "answer2": a2,
            }
            edit_account_json(new_uname, "w", json.dumps(new_data))
            status_data = "password_changed"
        elif saved_answer1 == ans1 or saved_answer2 == ans2:
            status_data = "one_correct"
        else:
            status_data = "both_wrong"
        return JsonResponse({"status": status_data}, safe=False)
    else:
        if check_user_existence(uname):
            sec_q = json.loads(get_registered_user_data(uname))
            rp_data = {
                "uname": uname,
                "favicon": get_fav_icon(),
                "q1": sec_q["question1"],
                "q2": sec_q["question2"],
            }
            return render(request, "resetpassword.html", rp_data)
        else:
            return redirect("/signup")

def render_signup_page(request):
    return render(request, "signup.html", {"favicon": get_fav_icon()})

def check_user_existence(user):
    if os.path.isdir(f"{BASE_DIR}//{DB_PATH}//{user}"):
        return True
    else:
        return False

def save_new_user_data(path, data):
    try:
        os.mkdir(path)
        with open(f"{path}//account.json", "w") as ud:
            ud.write(data)
        return True
    except Exception as e:
        print(e)
        return False

def check_signup(request):
    username = request.POST["username"]
    password = request.POST["password"]
    cpassword = request.POST["cpassword"]
    question1 = request.POST["question1"]
    answer1 = request.POST["answer1"]
    question2 = request.POST["question2"]
    answer2 = request.POST["answer2"]
    if username and password and cpassword and question1 and answer1 and question2 and answer2:
        signup_data = json.dumps({
            "password": password,
            "question1": question1,
            "answer1": answer1,
            "question2": question2,
            "answer2": answer2,
        })
        if not check_user_existence(username):
            new_user_path = f"{BASE_DIR}//{DB_PATH}//{username}"
            if save_new_user_data(new_user_path, signup_data):
                return JsonResponse({"status": "signup_success"}, safe=False)
            else:
                return JsonResponse({"status": "try_again"}, safe=False)
        else:
            return JsonResponse({"status": "user_exists"}, safe=False)
    return JsonResponse({"status": "error"}, safe=False)

def render_account_page(request):
    return render(request, "account.html", {"favicon": get_fav_icon()})

def save_notes_private(fdata):
    dict_dta = json.dumps(fdata)
    json_data = json.loads(dict_dta)
    p_u_name = json_data["uname"]
    p_date = json_data["date"]
    u_path = f"{BASE_DIR}//{DB_PATH}//{p_u_name}//{p_date}"
    os.mkdir(u_path)
    with open(f"{u_path}//note.json", "w") as sn:
        sn.write(dict_dta)

def save_notes_public(fdata):
    all_data = json.dumps(fdata)
    all_data = json.loads(all_data)
    note_date = all_data["date"]
    act_note = str(all_data["note"])
    u_name = all_data["uname"]
    fn_date = str(note_date).split()
    d_again = "-".join(fn_date[:5])
    dd_again = d_again.split(":")
    ddd_again = "-".join(dd_again)
    for_private_notes = {
        "pp": "public",
        "uname": u_name,
        "note": act_note,
        "date": ddd_again
    }
    save_notes_private(for_private_notes)
    p_path = f"{BASE_DIR}//public//{u_name}//"
    new_path = f"{p_path}{ddd_again}//"
    if os.path.isdir(p_path) == False:
        os.mkdir(p_path)
        os.mkdir(new_path)
        with open(f"{new_path}note.n", "wb") as nt:
            nt.write(act_note.encode())
    else:
        os.mkdir(new_path)
        with open(f"{new_path}note.n", "wb") as nt:
            nt.write(act_note.encode())

def save_notes(request):
    note = request.POST["note"]
    public_private = request.POST["for"]
    c_date = request.POST["date"]
    acc_data = request.POST["to"]
    uname = json.loads(acc_data)
    username = uname["uname"]
    final_data = {
        "note": note,
        "date": c_date,
        "uname": username
    }
    if public_private == "public":
        save_notes_public(final_data)
    else:
        fn_date = str(final_data["date"]).split()
        d_again = "-".join(fn_date[:5])
        dd_again = d_again.split(":")
        ddd_again = "-".join(dd_again)
        for_private_notes = {
            "pp": "private",
            "uname": final_data["uname"],
            "note": final_data["note"],
            "date": ddd_again
        }
        save_notes_private(for_private_notes)
    return JsonResponse({"status": "success"}, safe=False)
#made by bidhan acharya :)
#this much :)