import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Sparkles, Sun, Moon, Shield, Bell, LogOut, Trash2 } from "lucide-react";
import lawgptLogo from "@/assets/lawgpt-logo.png";

const Settings = () => {
  const navigate = useNavigate();
  const [theme, setTheme] = useState("auto");
  const [notif, setNotif] = useState(true);
  const [curPassword, setCurPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [delConfirm, setDelConfirm] = useState("");

  // Example: change password
  const handleChangePassword = (e) => {
    e.preventDefault();
    // Call backend API to update password
    alert("Password changed!");
    setCurPassword("");
    setNewPassword("");
  };

  // Example: delete account
  const handleDeleteAccount = (e) => {
    e.preventDefault();
    if (delConfirm === "DELETE") {
      // Call API to delete account
      alert("Your account has been deleted!");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-50 via-amber-50 to-white flex flex-col items-center py-10">
      <Card className="w-full max-w-2xl p-8 shadow-xl">
        <div className="flex gap-3 items-center mb-8">
          <img src={lawgptLogo} className="w-12 h-12" alt="LawGPT" />
          <h1 className="text-2xl font-bold text-blue-800">Settings</h1>
        </div>
        <section className="mb-8">
          <h2 className="font-semibold mb-2 flex items-center gap-2"><Sparkles className="w-5 h-5 text-amber-500" /> Theme</h2>
          <div className="flex gap-6 items-center">
            <Button 
              variant={theme === "auto" ? "default" : "outline"} 
              onClick={() => setTheme("auto")}
            >Auto</Button>
            <Button 
              variant={theme === "light" ? "default" : "outline"} 
              onClick={() => setTheme("light")}
            ><Sun className="w-5 h-5 mr-2" />Light</Button>
            <Button 
              variant={theme === "dark" ? "default" : "outline"} 
              onClick={() => setTheme("dark")}
            ><Moon className="w-5 h-5 mr-2" />Dark</Button>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="font-semibold mb-2 flex items-center gap-2"><Bell className="w-5 h-5 text-blue-600" /> Notification Preferences</h2>
          <div className="flex items-center gap-3">
            <Switch checked={notif} onCheckedChange={setNotif} />
            <span className="text-slate-800 text-sm">
              Email me about important account activity & legal news
            </span>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="font-semibold mb-3 flex items-center gap-2"><Shield className="w-5 h-5 text-blue-600" /> Change Password</h2>
          <form className="flex flex-col gap-4" onSubmit={handleChangePassword}>
            <Input
              type="password"
              placeholder="Current password"
              value={curPassword}
              onChange={(e) => setCurPassword(e.target.value)}
              required
            />
            <Input
              type="password"
              placeholder="New password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              minLength={6}
              required
            />
            <div>
              <Button type="submit" className="mt-2">Change Password</Button>
            </div>
          </form>
        </section>

        <section className="mb-5">
          <h2 className="font-semibold mb-2 flex items-center gap-2"><LogOut className="w-5 h-5 text-red-500" /> Session</h2>
          <Button
            variant="outline"
            className="text-red-600 border-red-400"
            onClick={() => {
              localStorage.removeItem("token");
              navigate("/login");
            }}
          >
            <LogOut className="w-4 h-4 mr-2" /> Log out
          </Button>
        </section>

        <section>
          <h2 className="font-semibold mb-2 flex items-center gap-2"><Trash2 className="w-5 h-5 text-red-500" /> Danger Zone</h2>
          <form onSubmit={handleDeleteAccount} className="flex flex-col gap-2">
            <span className="text-red-700 text-sm mb-2">
              Type <span className="font-bold">DELETE</span> below and press "Delete Account" to permanently erase your account.
            </span>
            <Input
              type="text"
              value={delConfirm}
              onChange={(e) => setDelConfirm(e.target.value)}
              placeholder='Type "DELETE" to confirm'
              className="border-red-300"
            />
            <Button
              type="submit"
              variant="destructive"
              disabled={delConfirm !== "DELETE"}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete Account
            </Button>
          </form>
        </section>
      </Card>
    </div>
  );
};

export default Settings;
