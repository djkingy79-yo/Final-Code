/* DO NOT UNDO — AppealChecklist component. All features in this file are approved and must be preserved. */
import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { 
  CheckCircle2, Circle, ChevronDown, ChevronRight
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Progress } from "./ui/progress";
import { Badge } from "./ui/badge";
import { toast } from "sonner";

const PHASE_CONFIG = {
  preparation: { label: "Preparation", color: "bg-slate-500" },
  grounds_identification: { label: "Identify Grounds", color: "bg-blue-500" },
  investigation: { label: "Investigation", color: "bg-purple-500" },
  documentation: { label: "Documentation", color: "bg-blue-500" },
  lodgement: { label: "Lodgement", color: "bg-emerald-500" },
  hearing: { label: "Hearing Prep", color: "bg-rose-500" }
};

const AppealChecklist = ({ caseId }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedPhases, setExpandedPhases] = useState(new Set(["preparation", "grounds_identification"]));

  useEffect(() => {
    fetchChecklist();
  }, [caseId]);

  const fetchChecklist = async () => {
    try {
      const response = await axios.get(`${API}/cases/${caseId}/checklist`);
      setItems(response.data);
    } catch (error) {
      console.error("Failed to fetch checklist:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleItem = async (itemId, isCompleted) => {
    try {
      await axios.patch(`${API}/cases/${caseId}/checklist/${itemId}`, {
        is_completed: !isCompleted
      });
      setItems(items.map(item => 
        item.item_id === itemId 
          ? { ...item, is_completed: !isCompleted }
          : item
      ));
    } catch (error) {
      toast.error("Failed to update item");
    }
  };

  const togglePhase = (phase) => {
    const newExpanded = new Set(expandedPhases);
    if (newExpanded.has(phase)) {
      newExpanded.delete(phase);
    } else {
      newExpanded.add(phase);
    }
    setExpandedPhases(newExpanded);
  };

  // Group items by phase
  const groupedItems = items.reduce((acc, item) => {
    if (!acc[item.phase]) acc[item.phase] = [];
    acc[item.phase].push(item);
    return acc;
  }, {});

  // Calculate progress
  const totalItems = items.length;
  const completedItems = items.filter(i => i.is_completed).length;
  const overallProgress = totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;

  const phaseOrder = ["preparation", "grounds_identification", "investigation", "documentation", "lodgement", "hearing"];

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-slate-200 rounded w-1/3"></div>
            <div className="h-2 bg-slate-200 rounded"></div>
            <div className="space-y-2">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-10 bg-slate-100 rounded"></div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card data-testid="appeal-checklist">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-slate-600" />
          Appeal Checklist
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Overall Progress */}
        <div className="mb-6">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-slate-600">Overall Progress</span>
            <span className="font-medium">{completedItems}/{totalItems} completed</span>
          </div>
          <Progress value={overallProgress} className="h-3" />
          <p className="text-xs text-slate-500 mt-1 text-right">{overallProgress}%</p>
        </div>

        {/* Phases */}
        <div className="space-y-3">
          {phaseOrder.map(phase => {
            const phaseItems = groupedItems[phase] || [];
            if (phaseItems.length === 0) return null;

            const phaseCompleted = phaseItems.filter(i => i.is_completed).length;
            const phaseProgress = Math.round((phaseCompleted / phaseItems.length) * 100);
            const isExpanded = expandedPhases.has(phase);
            const config = PHASE_CONFIG[phase] || { label: phase, color: "bg-slate-500" };

            return (
              <div key={phase} className="border border-slate-200 rounded-lg overflow-hidden">
                <button
                  onClick={() => togglePhase(phase)}
                  className="w-full p-3 flex items-center justify-between bg-slate-50 hover:bg-slate-100 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-slate-400" />
                    )}
                    <div className={`w-2 h-2 rounded-full ${config.color}`}></div>
                    <span className="font-medium text-slate-800">{config.label}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant={phaseProgress === 100 ? "default" : "outline"}
                      className={phaseProgress === 100 ? "bg-emerald-500" : ""}
                    >
                      {phaseCompleted}/{phaseItems.length}
                    </Badge>
                  </div>
                </button>
                
                {isExpanded && (
                  <div className="p-3 space-y-2 bg-white">
                    {phaseItems.map(item => (
                      <div 
                        key={item.item_id}
                        className={`flex items-start gap-3 p-2 rounded-lg transition-colors ${
                          item.is_completed ? 'bg-emerald-50' : 'hover:bg-slate-50'
                        }`}
                      >
                        <button
                          onClick={() => handleToggleItem(item.item_id, item.is_completed)}
                          className="mt-0.5 shrink-0"
                        >
                          {item.is_completed ? (
                            <CheckCircle2 className="w-5 h-5 text-emerald-600 fill-emerald-100" />
                          ) : (
                            <Circle className="w-5 h-5 text-slate-300 hover:text-emerald-500" />
                          )}
                        </button>
                        <div className="flex-1 min-w-0">
                          <p className={`text-sm font-medium ${item.is_completed ? 'text-slate-500 line-through' : 'text-slate-800'}`}>
                            {item.title}
                          </p>
                          {item.description && (
                            <p className={`text-xs mt-0.5 ${item.is_completed ? 'text-slate-400' : 'text-slate-500'}`}>
                              {item.description}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default AppealChecklist;
