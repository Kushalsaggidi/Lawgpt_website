import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  ArrowLeft, 
  Edit2, 
  Award, 
  TrendingUp, 
  Calendar, 
  Target, 
  User, 
  Mail, 
  Shield, 
  Clock, 
  Star,
  Activity,
  BookOpen,
  Zap,
  CheckCircle,
  Settings,
  Bell
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import lawgptLogo from "@/assets/lawgpt-logo.png";

const Profile = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState("");
  const [bio, setBio] = useState("");
  const [email, setEmail] = useState("");
  const userInitial = email ? email[0].toUpperCase() : "U";
  const [memberSince, setMemberSince] = useState("");

  const [stats, setStats] = useState({
    totalQueries: 0,
    favoriteModel: "LawGPT",
    accountAge: "",
    currentStreak: "",
    accuracy: 0,
    responseTime: 0,
    satisfaction: 0,
  });

  const [recentActivity, setRecentActivity] = useState([
    { id: 1, action: "Legal query about contract law", timestamp: "2 hours ago", type: "query" },
    { id: 2, action: "Updated profile information", timestamp: "1 day ago", type: "profile" },
    { id: 3, action: "Changed notification settings", timestamp: "3 days ago", type: "settings" },
    { id: 4, action: "Completed legal research session", timestamp: "1 week ago", type: "research" },
  ]);

  const achievements = [
    { name: "First Query", icon: Target, earned: true, description: "Asked your first legal question" },
    { name: "Legal Explorer", icon: BookOpen, earned: true, description: "Completed 10 queries" },
    { name: "Active User", icon: Activity, earned: true, description: "Used the platform for 7 days" },
    { name: "Power User", icon: Zap, earned: false, description: "Complete 100 queries" },
    { name: "Legal Scholar", icon: Award, earned: false, description: "Achieve 95% accuracy" },
    { name: "Daily Learner", icon: Star, earned: true, description: "Used platform 30 days in a row" },
  ];

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }
    const load = async () => {
      try {
        const res = await fetch("http://localhost:5000/api/profile", {
          headers: { "Authorization": "Bearer " + token },
        });
        if (res.ok) {
          const data = await res.json();
          setName(data.name || "");
          setBio(data.bio || "");
          setEmail(data.email || "");
          setMemberSince(data.memberSince || "");
          const s = data.stats || {};
          setStats({
            totalQueries: s.totalQueries || 0,
            favoriteModel: s.favoriteModel || "LawGPT",
            accountAge: s.accountAge || "",
            currentStreak: s.currentStreak || "",
            accuracy: s.accuracy || 0,
            responseTime: s.responseTime || 0,
            satisfaction: s.satisfaction || 0,
          });
        }
      } catch (err) {
        console.error("Profile load error:", err);
      }
    };
    load();
  }, [navigate]);

  const handleSave = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      toast({ 
        title: "Error", 
        description: "Not logged in", 
        variant: "destructive" 
      });
      return;
    }
    try {
      const res = await fetch("http://localhost:5000/api/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + token,
        },
        body: JSON.stringify({ name, bio }),
      });
      if (res.ok) {
        setIsEditing(false);
        toast({ title: "Profile Updated", description: "Your profile has been updated" });
      } else {
        const error = await res.json();
        toast({ 
          title: "Error", 
          description: error.error || "Failed to update profile", 
          variant: "destructive" 
        });
      }
    } catch (err) {
      console.error("Profile save error:", err);
      toast({ 
        title: "Error", 
        description: "Failed to update profile. Please try again.", 
        variant: "destructive" 
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                className="text-slate-600 hover:text-blue-600 hover:bg-blue-50"
                onClick={() => navigate("/dashboard")}
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Dashboard
              </Button>
            </div>

            <div className="flex items-center gap-3">
              <img src={lawgptLogo} alt="LawGPT" className="w-8 h-8" />
              <span className="text-xl font-bold text-blue-600">LawGPT</span>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Breadcrumb */}
        <nav className="flex items-center space-x-2 text-sm text-slate-500 mb-8">
          <span>Dashboard</span>
          <span>›</span>
          <span className="text-blue-600 font-medium">Profile</span>
        </nav>

        {/* Profile Header */}
        <Card className="p-8 mb-8 shadow-lg border-0 bg-white/70 backdrop-blur-sm">
          <div className="flex flex-col lg:flex-row items-start gap-8">
            <div className="relative">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-white flex items-center justify-center text-2xl font-bold shadow-lg">
                {userInitial}
              </div>
              <button 
                className="absolute -bottom-2 -right-2 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center hover:bg-blue-700 transition-colors shadow-lg"
                title="Edit profile picture"
                aria-label="Edit profile picture"
              >
                <Edit2 className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1">
              {isEditing ? (
                <div className="space-y-6">
                  <div>
                    <Label htmlFor="name" className="text-sm font-medium text-slate-700">Full Name</Label>
                    <Input
                      id="name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="mt-1 text-lg"
                      placeholder="Enter your full name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="bio" className="text-sm font-medium text-slate-700">Bio</Label>
                    <Textarea
                      id="bio"
                      value={bio}
                      onChange={(e) => setBio(e.target.value)}
                      className="mt-1"
                      placeholder="Tell us about yourself..."
                      rows={3}
                    />
                  </div>
                  <div className="flex gap-3">
                    <Button
                      onClick={handleSave}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      Save Changes
                    </Button>
                    <Button variant="outline" onClick={() => setIsEditing(false)}>
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <div>
                  <h1 className="text-3xl font-bold text-slate-900 mb-2">{name || "User"}</h1>
                  <p className="text-slate-600 mb-4 text-lg">{bio || "No bio available"}</p>
                  <div className="flex items-center gap-6 text-sm text-slate-500">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      Member since {memberSince || "Unknown"}
                    </div>
                    <div className="flex items-center gap-2">
                      <Mail className="w-4 h-4" />
                      {email}
                    </div>
                  </div>
                  <div className="mt-4">
                    <Button
                      variant="outline"
                      size="sm"
                      className="border-blue-200 text-blue-600 hover:bg-blue-50"
                      onClick={() => setIsEditing(true)}
                    >
                      <Edit2 className="w-4 h-4 mr-2" />
                      Edit Profile
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </Card>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6 text-center hover:shadow-lg transition-all duration-200 border-0 bg-white/70 backdrop-blur-sm">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Target className="w-6 h-6 text-blue-600" />
            </div>
            <p className="text-2xl font-bold text-slate-900 mb-1">{stats.totalQueries}</p>
            <p className="text-sm text-slate-600">Total Queries</p>
          </Card>

          <Card className="p-6 text-center hover:shadow-lg transition-all duration-200 border-0 bg-white/70 backdrop-blur-sm">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <p className="text-lg font-bold text-slate-900 mb-1">{stats.favoriteModel}</p>
            <p className="text-sm text-slate-600">Favorite Model</p>
          </Card>

          <Card className="p-6 text-center hover:shadow-lg transition-all duration-200 border-0 bg-white/70 backdrop-blur-sm">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Clock className="w-6 h-6 text-purple-600" />
            </div>
            <p className="text-2xl font-bold text-slate-900 mb-1">{stats.accountAge}</p>
            <p className="text-sm text-slate-600">Account Age</p>
          </Card>

          <Card className="p-6 text-center hover:shadow-lg transition-all duration-200 border-0 bg-white/70 backdrop-blur-sm">
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Award className="w-6 h-6 text-orange-600" />
            </div>
            <p className="text-2xl font-bold text-slate-900 mb-1">{stats.currentStreak}</p>
            <p className="text-sm text-slate-600">Current Streak</p>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Activity */}
          <div className="lg:col-span-2">
            <Card className="p-6 shadow-lg border-0 bg-white/70 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-blue-600" />
                  Recent Activity
                </h2>
                <Button variant="ghost" size="sm" className="text-blue-600 hover:text-blue-700">
                  View All
                </Button>
              </div>
              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                      {activity.type === 'query' && <BookOpen className="w-4 h-4 text-blue-600" />}
                      {activity.type === 'profile' && <User className="w-4 h-4 text-blue-600" />}
                      {activity.type === 'settings' && <Settings className="w-4 h-4 text-blue-600" />}
                      {activity.type === 'research' && <Target className="w-4 h-4 text-blue-600" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900">{activity.action}</p>
                      <p className="text-xs text-slate-500">{activity.timestamp}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Achievements */}
          <div>
            <Card className="p-6 shadow-lg border-0 bg-white/70 backdrop-blur-sm">
              <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                <Award className="w-5 h-5 text-blue-600" />
                Achievements
              </h2>
              <div className="space-y-4">
                {achievements.map((achievement, index) => {
                  const IconComponent = achievement.icon;
                  return (
                    <div
                      key={index}
                      className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-200 ${
                        achievement.earned
                          ? "bg-blue-50 border border-blue-200 hover:bg-blue-100"
                          : "bg-slate-50 border border-slate-200 opacity-60"
                      }`}
                    >
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        achievement.earned ? "bg-blue-100" : "bg-slate-200"
                      }`}>
                        <IconComponent className={`w-5 h-5 ${
                          achievement.earned ? "text-blue-600" : "text-slate-400"
                        }`} />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-slate-900">{achievement.name}</p>
                        <p className="text-xs text-slate-500">{achievement.description}</p>
                      </div>
                      {achievement.earned && (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      )}
                    </div>
                  );
                })}
              </div>
            </Card>
          </div>
        </div>

        {/* Account Information */}
        <Card className="p-6 shadow-lg mt-8 border-0 bg-white/70 backdrop-blur-sm">
          <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
            <Shield className="w-5 h-5 text-blue-600" />
            Account Information
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label className="text-sm font-medium text-slate-700">Email Address</Label>
              <div className="mt-1 flex items-center gap-2">
                <Mail className="w-4 h-4 text-slate-400" />
                <p className="text-slate-900">{email}</p>
              </div>
              <p className="text-xs text-slate-500 mt-1">Email cannot be changed for security reasons</p>
            </div>
            <div>
              <Label className="text-sm font-medium text-slate-700">Account Status</Label>
              <div className="mt-1 flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <p className="text-slate-900">Active</p>
              </div>
              <p className="text-xs text-slate-500 mt-1">Your account is in good standing</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Profile;
