import { useEffect, useState } from "react";
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

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;
    const load = async () => {
      try {
        const res = await fetch("http://localhost:5000/api/settings", {
          headers: { "Authorization": "Bearer " + token },
        });
        if (res.ok) {
          const data = await res.json();
          setTheme(data.theme || "auto");
          setNotif(Boolean(data.notifications?.enabled));
          console.log("Settings loaded:", data);
        } else {
          const error = await res.json();
          console.error("Settings load error:", error);
          alert(`Error loading settings: ${error.error || "Unknown error"}`);
        }
      } catch (err) {
        console.error("Settings load error:", err);
        alert("Failed to load settings. Please check your connection.");
      }
    };
    load();
  }, []);

  const persistSettings = async (next: { theme?: string; notifications?: { enabled?: boolean } }) => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Not logged in");
      return;
    }
    try {
      const res = await fetch("http://localhost:5000/api/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
        body: JSON.stringify(next),
      });
      if (res.ok) {
        console.log("Settings updated successfully");
      } else {
        const error = await res.json();
        alert(`Error: ${error.error || "Failed to update settings"}`);
      }
    } catch (err) {
      console.error("Settings update error:", err);
      alert("Failed to update settings. Please try again.");
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Not logged in");
      return;
    }
    if (!newPassword || newPassword.length < 6) {
      alert("Password must be at least 6 characters long");
      return;
    }
    try {
      const res = await fetch("http://localhost:5000/api/change-password", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
        body: JSON.stringify({ new_password: newPassword })
      });
      if (res.ok) {
        setCurPassword("");
        setNewPassword("");
        alert("Password changed successfully!");
      } else {
        const error = await res.json();
        alert(`Error: ${error.error || "Failed to change password"}`);
      }
    } catch (err) {
      console.error("Password change error:", err);
      alert("Failed to change password. Please try again.");
    }
  };

  // Delete account
  const handleDeleteAccount = async (e) => {
    e.preventDefault();
    if (delConfirm === "DELETE") {
      const token = localStorage.getItem("token");
      try {
        const res = await fetch("http://localhost:5000/api/delete-account", {
          method: "POST",
          headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
          body: JSON.stringify({ confirmation: "DELETE" })
        });
        if (res.ok) {
          localStorage.removeItem("token");
          alert("Your account has been deleted successfully!");
          navigate("/login");
        } else {
          const error = await res.json();
          alert(`Error: ${error.error}`);
        }
      } catch (err) {
        alert("Failed to delete account. Please try again.");
      }
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
              onClick={async () => { 
                setTheme("auto"); 
                await persistSettings({ theme: "auto" }); 
                alert("Theme changed to Auto");
              }}
            >Auto</Button>
            <Button
              variant={theme === "light" ? "default" : "outline"}
              onClick={async () => { 
                setTheme("light"); 
                await persistSettings({ theme: "light" }); 
                alert("Theme changed to Light");
              }}
            ><Sun className="w-5 h-5 mr-2" />Light</Button>
            <Button
              variant={theme === "dark" ? "default" : "outline"}
              onClick={async () => { 
                setTheme("dark"); 
                await persistSettings({ theme: "dark" }); 
                alert("Theme changed to Dark");
              }}
            ><Moon className="w-5 h-5 mr-2" />Dark</Button>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="font-semibold mb-2 flex items-center gap-2"><Bell className="w-5 h-5 text-blue-600" /> Notification Preferences</h2>
          <div className="flex items-center gap-3">
            <Switch checked={notif} onCheckedChange={async (v) => { 
              setNotif(!!v); 
              await persistSettings({ notifications: { enabled: !!v } }); 
              alert(`Notifications ${!!v ? 'enabled' : 'disabled'}`);
            }} />
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
