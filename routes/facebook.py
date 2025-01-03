from flask import Blueprint, render_template, request, redirect, url_for
from database_init import mysql
from post_fb import get_account

facebook_bp = Blueprint("facebook", __name__)


@facebook_bp.route("/account_fb/")
def account_fb():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, email, access_token FROM facebook_accounts")
    accounts = cursor.fetchall()
    cursor.close()
    return render_template("account_fb.html", accounts=accounts)


@facebook_bp.route("/account_fb/add_account", methods=["POST"])
def add_fb_account():
    if request.method == "POST":
        email = request.form["email"]
        access_token = request.form["access_token"]
        cursor = mysql.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO facebook_accounts (email, access_token) VALUES (%s, %s)",
                (email, access_token),
            )
            mysql.connection.commit()
            print("Facebook account added successfully!", "success")
        except Exception as e:
            print(f"Error: {e}", "danger")
        finally:
            cursor.close()
        return redirect(url_for("facebook.account_fb"))


@facebook_bp.route("/account_fb/delete_account/<int:id>", methods=["GET", "POST"])
def delete_fb_account(id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM facebook_accounts WHERE id = %s", (id,))
        mysql.connection.commit()
        print("Facebook account deleted successfully!", "success")
    except Exception as e:
        print(f"Error: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for("facebook.account_fb"))


@facebook_bp.route("/account_fb/get_pages", methods=["POST"])
def get_pages():
    access_token = request.form.get("access_token")
    id = request.form.get("id")

    if not access_token:
        print("Access token không được cung cấp.", "danger")
        error_message = "Access token không được cung cấp."
        return render_template("error.html", error_message=error_message)

    try:
        # Gọi hàm get_account để lấy danh sách các trang
        pages = get_account(access_token, id)
        if pages:
            print("Lấy thông tin các trang thành công")
            return redirect(url_for("pages.show_pages"))
        else:
            print("Không thể lấy thông tin trang.", "danger")
            error_message = "Không thể lấy thông tin trang."
            return render_template("error.html", error_message=error_message)
    except Exception as e:
        print(f"Lỗi: {e}", "danger")
        error_message = f"Lỗi: {e}"
        return render_template("error.html", error_message=error_message)
