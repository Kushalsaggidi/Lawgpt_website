import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { ArrowLeft, Edit2, Award, TrendingUp, Calendar, Target } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import lawgptLogo from "@/assets/lawgpt-logo.png";

const Profile = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState("John Doe");
  const [bio, setBio] = useState("Legal professional specializing in corporate law");
  const email = "john.doe@example.com";
  const userInitial = email[0].toUpperCase();
  const memberSince = "October 2025";

  const stats = {
    totalQueries: 156,
    favoriteModel: "LawGPT Fine-tuned",
    accountAge: "2 months",
    currentStreak: "7 days",
  };

  const achievements = [
    { name: "First Query", icon: "🎯", earned: true },
    { name: "100 Queries", icon: "💯", earned: true },
    { name: "1 Month Active", icon: "📅", earned: true },
    { name: "Power User", icon: "⚡", earned: false },
    { name: "Legal Scholar", icon: "📚", earned: false },
    { name: "Daily Learner", icon: "🌟", earned: true },
  ];

  const handleSave = () => {
    setIsEditing(false);
    toast({
      title: "Profile Updated",
      description: "Your profile has been successfully updated",
    });
  };

  return (
    <div className="min-h-screen bg-cream">
      {/* Header */}
      <header className="bg-primary text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                className="text-white hover:text-gold hover:bg-white/10"
                onClick={() => navigate("/dashboard")}
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Dashboard
              </Button>
            </div>

            <div className="flex items-center gap-3">
              <img src={lawgptLogo} alt="LawGPT" className="w-8 h-8" />
              <span className="text-xl font-bold text-gold">LawGPT</span>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Breadcrumb */}
        <p className="text-sm text-muted-foreground mb-6">
          Dashboard <span className="text-gold">›</span> Profile
        </p>

        {/* Profile Header Card */}
        <Card className="p-8 shadow-gold mb-8 animate-fade-in">
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="relative">
              <div className="w-32 h-32 rounded-full bg-gold text-primary flex items-center justify-center text-5xl font-bold shadow-lg">
                {userInitial}
              </div>
              <button className="absolute bottom-0 right-0 w-10 h-10 bg-primary text-white rounded-full flex items-center justify-center hover:bg-primary/90 transition-smooth shadow-lg">
                <Edit2 className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 text-center md:text-left">
              {isEditing ? (
                <div className="space-y-4">
                  <Input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="text-xl font-bold"
                  />
                  <Textarea
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                    className="text-muted-foreground"
                  />
                  <div className="flex gap-3">
                    <Button
                      onClick={handleSave}
                      className="bg-gold hover:bg-gold/90 text-primary"
                    >
                      Save Changes
                    </Button>
                    <Button variant="outline" onClick={() => setIsEditing(false)}>
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <>
                  <h1 className="text-3xl font-bold text-primary mb-2">{name}</h1>
                  <p className="text-lg text-muted-foreground mb-4">{bio}</p>
                  <div className="flex items-center gap-6 justify-center md:justify-start text-sm">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Calendar className="w-4 h-4 text-gold" />
                      Member since {memberSince}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      className="border-gold text-gold hover:bg-gold hover:text-primary"
                      onClick={() => setIsEditing(true)}
                    >
                      <Edit2 className="w-4 h-4 mr-2" />
                      Edit Profile
                    </Button>
                  </div>
                </>
              )}
            </div>
          </div>
        </Card>

        {/* Statistics Grid */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card className="p-6 text-center hover:shadow-lg transition-smooth animate-scale-in">
            <Target className="w-8 h-8 text-gold mx-auto mb-3" />
            <p className="text-3xl font-bold text-primary mb-1">{stats.totalQueries}</p>
            <p className="text-sm text-muted-foreground">Total Queries</p>
          </Card>

          <Card className="p-6 text-center hover:shadow-lg transition-smooth animate-scale-in">
            <TrendingUp className="w-8 h-8 text-gold mx-auto mb-3" />
            <p className="text-lg font-bold text-primary mb-1">{stats.favoriteModel}</p>
            <p className="text-sm text-muted-foreground">Favorite Model</p>
          </Card>

          <Card className="p-6 text-center hover:shadow-lg transition-smooth animate-scale-in">
            <Calendar className="w-8 h-8 text-gold mx-auto mb-3" />
            <p className="text-3xl font-bold text-primary mb-1">{stats.accountAge}</p>
            <p className="text-sm text-muted-foreground">Account Age</p>
          </Card>

          <Card className="p-6 text-center hover:shadow-lg transition-smooth animate-scale-in">
            <Award className="w-8 h-8 text-gold mx-auto mb-3" />
            <p className="text-3xl font-bold text-primary mb-1">{stats.currentStreak}</p>
            <p className="text-sm text-muted-foreground">Current Streak</p>
          </Card>
        </div>

        {/* Achievement Badges */}
        <Card className="p-8 shadow-lg animate-fade-in">
          <h2 className="text-2xl font-bold text-primary mb-6 flex items-center gap-2">
            <Award className="w-6 h-6 text-gold" />
            Achievement Badges
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {achievements.map((achievement, index) => (
              <div
                key={index}
                className={`p-4 rounded-xl text-center transition-smooth ${
                  achievement.earned
                    ? "bg-gold/10 border-2 border-gold hover:scale-105 cursor-pointer"
                    : "bg-gray-100 border-2 border-gray-200 opacity-50"
                }`}
              >
                <div className="text-4xl mb-2">{achievement.icon}</div>
                <p className="text-xs font-semibold text-primary">{achievement.name}</p>
                {achievement.earned && (
                  <p className="text-xs text-gold mt-1">✓ Earned</p>
                )}
              </div>
            ))}
          </div>
        </Card>

        {/* Activity Graph Placeholder */}
        <Card className="p-8 shadow-lg mt-8 animate-fade-in">
          <h2 className="text-2xl font-bold text-primary mb-6">Activity Over Time</h2>
          <div className="h-64 bg-gradient-to-r from-secondary to-accent rounded-lg flex items-center justify-center">
            <p className="text-muted-foreground">Activity graph visualization coming soon</p>
          </div>
        </Card>

        {/* Personal Information */}
        <Card className="p-8 shadow-lg mt-8 animate-fade-in">
          <h2 className="text-2xl font-bold text-primary mb-6">Personal Information</h2>
          <div className="space-y-4">
            <div>
              <Label className="text-muted-foreground">Email Address</Label>
              <p className="text-lg font-semibold text-primary">{email}</p>
              <p className="text-sm text-muted-foreground">Email cannot be changed for security</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Profile;
