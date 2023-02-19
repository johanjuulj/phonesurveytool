@pages.get("/sms/<string:_id>")
def sms(_id:str):
    sms_data = current_app.db.Questions.find_one({"_id": _id})
    sms = SMS(**sms_data)
    return render_template("sms_details.html", sms=sms)







