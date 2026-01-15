import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  Cell,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tooltip as UITooltip } from '@/components/ui/tooltip';
import { MetricResult } from '@/lib/api';
import { CheckCircle2, AlertTriangle, XCircle, ChevronDown, ChevronUp, HelpCircle } from 'lucide-react';
import { useState, useMemo, memo } from 'react';

interface MetricVisualizationProps {
  metric: MetricResult;
}

const COLORS = ['#f97316', '#fbbf24', '#ef4444', '#fb923c', '#fcd34d', '#dc2626'];

const AssessmentBadge = memo(({ assessment }: { assessment: string }) => {
  const config = {
    Fair: { icon: CheckCircle2, color: 'text-orange-100', bg: 'bg-orange-600', border: 'border-orange-500' },
    Warning: { icon: AlertTriangle, color: 'text-amber-100', bg: 'bg-amber-600', border: 'border-amber-500' },
    Violation: { icon: XCircle, color: 'text-red-100', bg: 'bg-red-600', border: 'border-red-500' },
  };

  const { icon: Icon, color, bg, border } = config[assessment as keyof typeof config] || config.Warning;

  return (
    <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${bg} ${border} border`}>
      <Icon className={`h-5 w-5 ${color}`} />
      <span className={`text-sm font-semibold ${color}`}>{assessment}</span>
    </div>
  );
});

const BarChartVisualization = memo(({ data }: { data: any }) => {
  const chartData = useMemo(() => 
    Object.entries(data).map(([name, value]: [string, any]) => ({
      name,
      value: typeof value === 'number' ? value : value?.rate || 0,
    }))
  , [data]);

  // Calculate max value for threshold line
  const maxValue = useMemo(() => Math.max(...chartData.map(d => d.value)), [chartData]);
  const thresholdValue = maxValue * 0.1; // 10% threshold

  // Determine color based on fairness (using difference from mean as proxy)
  const mean = useMemo(() => chartData.reduce((sum, d) => sum + d.value, 0) / chartData.length, [chartData]);
  const getBarColor = useMemo(() => (value: number) => {
    const diffFromMean = Math.abs(value - mean) / mean;
    if (diffFromMean < 0.1) return '#22c55e'; // green - fair
    if (diffFromMean < 0.2) return '#eab308'; // yellow - warning
    return '#ef4444'; // red - violation
  }, [mean]);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
        <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
        <Tooltip 
          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }}
          labelStyle={{ color: '#e2e8f0' }}
          formatter={(value: any) => [
            `${(value * 100).toFixed(1)}%`,
            'Value'
          ]}
        />
        <Legend wrapperStyle={{ color: '#94a3b8' }} />
        <Bar dataKey="value" fill="#fb923c" label={{ position: 'top', fill: '#e2e8f0', formatter: (value: number) => `${(value * 100).toFixed(1)}%` }} animationDuration={300} isAnimationActive={false}>
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={getBarColor(entry.value)} />
          ))}
        </Bar>
        {/* Reference line for 10% threshold if applicable */}
        {thresholdValue > 0 && (
          <line 
            x1="0" 
            y1={`${(1 - thresholdValue / maxValue) * 100}%`} 
            x2="100%" 
            y2={`${(1 - thresholdValue / maxValue) * 100}%`} 
            stroke="#fb923c" 
            strokeDasharray="5 5" 
            strokeWidth="2"
          />
        )}
      </BarChart>
    </ResponsiveContainer>
  );
});

const HeatmapVisualization = memo(({ bins, data }: { bins?: string[]; data: Record<string, number[]> }) => {
  const groups = useMemo(() => Object.keys(data || {}), [data]);
  if (!groups.length) {
    return <div className="text-slate-500">No calibration data available</div>;
  }

  const numericValues = useMemo(() => groups.flatMap((group) =>
    (data[group] || []).filter((value) => typeof value === 'number')
  ), [groups, data]);

  const minValue = useMemo(() => Math.min(...numericValues, 0), [numericValues]);
  const maxValue = useMemo(() => Math.max(...numericValues, 1), [numericValues]);
  const fallbackBins = useMemo(() => (data[groups[0]] || []).map((_, idx) => `Bin ${idx + 1}`), [data, groups]);
  const binLabels = useMemo(() => bins && bins.length ? bins : fallbackBins, [bins, fallbackBins]);

  const getCellColor = (value: number) => {
    const normalized = maxValue === minValue ? 0 : (value - minValue) / (maxValue - minValue);
    // Orange to Red gradient: hue 25 (orange) to 0 (red), higher values are more red
    const hue = 25 - normalized * 25;
    const saturation = 85 + normalized * 10;
    const lightness = 65 - normalized * 25;
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="border border-slate-600 px-3 py-2 text-left text-xs font-semibold text-slate-300 bg-slate-800/50">Group</th>
            {binLabels.map((label, idx) => (
              <th key={idx} className="border border-slate-600 px-3 py-2 text-xs font-semibold text-slate-300 bg-slate-800/50">
                {label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {groups.map((group) => (
            <tr key={group}>
              <td className="border border-slate-600 px-3 py-2 text-sm font-medium bg-slate-800/50 text-slate-200">{group}</td>
              {binLabels.map((_, idx) => {
                const rawValue = data[group]?.[idx];
                const value = typeof rawValue === 'number' ? rawValue : 0;
                return (
                  <td
                    key={`${group}-${idx}`}
                    className="border border-slate-600 px-2 py-2 text-center text-xs font-bold text-white"
                    style={{ backgroundColor: getCellColor(value), textShadow: '0 1px 2px rgba(0,0,0,0.5)' }}
                  >
                    {value.toFixed(2)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex items-center gap-2 mt-3 text-xs text-slate-300">
        <span>Low actual rate</span>
        <div className="h-2 flex-1 bg-gradient-to-r from-orange-300 via-orange-500 to-red-600 rounded"></div>
        <span>High actual rate</span>
      </div>
    </div>
  );
});

const ScatterPlotVisualization = memo(({ data }: { data: any }) => {
  const groups = useMemo(() => Object.entries(data), [data]);

  return (
    <ResponsiveContainer width="100%" height={350}>
      <ScatterChart margin={{ top: 20, right: 30, bottom: 60, left: 60 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis 
          type="number" 
          dataKey="fpr" 
          name="False Positive Rate" 
          label={{ value: 'False Positive Rate', position: 'insideBottom', offset: -10, fill: '#94a3b8' }}
          domain={[0, 1]}
          stroke="#94a3b8"
          tick={{ fill: '#94a3b8' }}
        />
        <YAxis 
          type="number" 
          dataKey="tpr" 
          name="True Positive Rate" 
          label={{ value: 'True Positive Rate', angle: -90, position: 'insideLeft', offset: 10, fill: '#94a3b8' }}
          domain={[0, 1]}
          stroke="#94a3b8"
          tick={{ fill: '#94a3b8' }}
        />
        <Tooltip 
          formatter={(value: any) => value.toFixed(4)}
          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }}
          labelStyle={{ color: '#e2e8f0' }}
        />
        <Legend 
          wrapperStyle={{ color: '#94a3b8' }} 
          verticalAlign="top"
          height={36}
        />
        {groups.map(([name, value]: [string, any], index) => (
          <Scatter
            key={name}
            name={name}
            data={[{ fpr: value.fpr || 0, tpr: value.tpr || 0, name }]}
            fill={COLORS[index % COLORS.length]}
            shape="circle"
            line={false}
            isAnimationActive={false}
          />
        ))}
      </ScatterChart>
    </ResponsiveContainer>
  );
});

const MetricValueDisplay = memo(({ value }: { value: any }) => {
  if (typeof value === 'number') {
    return (
      <div className="text-center p-6 bg-slate-900/50 border border-slate-700/50 rounded-lg backdrop-blur-sm">
        <div className="text-4xl font-bold text-orange-400">{value.toFixed(4)}</div>
        <p className="text-sm text-slate-400 mt-2">Metric Value</p>
      </div>
    );
  }

  if (typeof value === 'object' && value !== null) {
    return (
      <div className="space-y-2">
        {Object.entries(value).map(([key, val]: [string, any]) => (
          <div key={key} className="flex justify-between items-center p-3 bg-slate-800/50 border border-slate-600/50 rounded">
            <span className="font-medium text-slate-200">{key}</span>
            <span className="text-orange-400 font-mono">
              {typeof val === 'number' ? val.toFixed(4) : JSON.stringify(val)}
            </span>
          </div>
        ))}
      </div>
    );
  }

  return <div className="text-slate-500">No data available</div>;
});

export const MetricVisualization = memo(({ metric }: MetricVisualizationProps) => {
  const vizData = metric.visualization_data;
  const vizType = vizData?.visualization_type;
  const isProblematic = metric.fairness_assessment !== 'Fair';
  const [expandedSections, setExpandedSections] = useState({
    whatThisMeans: !isProblematic,
    rootCauses: false,
    actions: false,
  });

  const toggleSection = (section: 'whatThisMeans' | 'rootCauses' | 'actions') => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  return (
    <Card className={`mb-6 md:mb-8 backdrop-blur-md shadow-xl transition-all duration-300 ${
      metric.fairness_assessment === 'Violation'
        ? 'bg-red-950/30 border-red-500/60 hover:border-red-500/80 hover:shadow-red-500/20'
        : metric.fairness_assessment === 'Warning'
        ? 'bg-amber-950/30 border-amber-500/60 hover:border-amber-500/80 hover:shadow-amber-500/20'
        : 'bg-slate-800/60 border-slate-700/50 hover:border-slate-600/70'
    }`}>
      <CardHeader className="pb-4">
        <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-3">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <CardTitle className="text-base md:text-xl font-bold text-slate-100">{metric.explanation.display_name}</CardTitle>
              <UITooltip content={metric.explanation.definition}>
                <HelpCircle className="h-4 w-4 text-slate-400 hover:text-slate-300 cursor-help transition-colors" />
              </UITooltip>
            </div>
            <CardDescription className="mt-2 text-sm text-slate-400 leading-relaxed">{metric.explanation.definition}</CardDescription>
          </div>
          <AssessmentBadge assessment={metric.fairness_assessment} />
        </div>
      </CardHeader>
      <CardContent className="px-5 md:px-7">
        {/* Show Risk/Violation Alert Box at the top if problematic */}
        {isProblematic && (
          <div className={`mb-5 md:mb-7 p-4 md:p-5 rounded-xl border-l-4 backdrop-blur-sm shadow-lg ${
            metric.fairness_assessment === 'Violation' 
              ? 'bg-gradient-to-r from-red-950/60 to-red-950/30 border-red-500' 
              : 'bg-gradient-to-r from-amber-950/60 to-amber-950/30 border-amber-500'
          }`}>
            <div className="flex items-start gap-3">
              {metric.fairness_assessment === 'Violation' ? (
                <XCircle className="h-8 w-8 text-red-400 flex-shrink-0 mt-1" />
              ) : (
                <AlertTriangle className="h-8 w-8 text-amber-400 flex-shrink-0 mt-1" />
              )}
              <div className="flex-1">
                <h3 className={`font-bold text-lg md:text-xl mb-3 ${
                  metric.fairness_assessment === 'Violation' ? 'text-red-300' : 'text-amber-300'
                }`}>
                  {metric.fairness_assessment === 'Violation' ? 'Fairness Violation Detected' : 'Fairness Risk Detected'}
                </h3>
                
                {metric.explanation.what_this_means && (
                  <div className="mb-3">
                    <button
                      onClick={() => toggleSection('whatThisMeans')}
                      className="flex items-center gap-2 w-full text-left"
                    >
                      <p className={`font-semibold text-sm ${
                        metric.fairness_assessment === 'Violation' ? 'text-red-300' : 'text-amber-300'
                      }`}>
                        What This Means
                      </p>
                      {expandedSections.whatThisMeans ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </button>
                    {expandedSections.whatThisMeans && (
                      <p className={`text-sm mt-2 ${
                        metric.fairness_assessment === 'Violation' ? 'text-red-200' : 'text-amber-200'
                      }`}>
                        {metric.explanation.what_this_means}
                      </p>
                    )}
                  </div>
                )}

                {metric.explanation.what_is_wrong && (
                  <div className="mb-3">
                    <p className={`font-semibold text-sm ${
                      metric.fairness_assessment === 'Violation' ? 'text-red-300' : 'text-amber-300'
                    }`}>
                      What Is Wrong:
                    </p>
                    <p className={`text-sm mt-1 ${
                      metric.fairness_assessment === 'Violation' ? 'text-red-200' : 'text-amber-200'
                    }`}>
                      {metric.explanation.what_is_wrong}
                    </p>
                  </div>
                )}

                {metric.explanation.root_causes && metric.explanation.root_causes.length > 0 && (
                  <div className="mb-3">
                    <button
                      onClick={() => toggleSection('rootCauses')}
                      className="flex items-center gap-2 w-full text-left"
                    >
                      <p className={`font-semibold text-sm ${
                        metric.fairness_assessment === 'Violation' ? 'text-red-300' : 'text-amber-300'
                      }`}>
                        Likely Root Causes
                      </p>
                      {expandedSections.rootCauses ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </button>
                    {expandedSections.rootCauses && (
                      <ul className="list-disc list-inside space-y-1 mt-2">
                        {metric.explanation.root_causes.map((cause: string, idx: number) => (
                          <li key={idx} className={`text-sm ${
                            metric.fairness_assessment === 'Violation' ? 'text-red-200' : 'text-amber-200'
                          }`}>
                            {cause}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}

                {metric.explanation.recruiter_actions && metric.explanation.recruiter_actions.length > 0 && (
                  <div className="mt-3">
                    <button
                      onClick={() => toggleSection('actions')}
                      className="flex items-center gap-2 w-full text-left mb-2"
                    >
                      <p className="font-semibold text-sm text-orange-300">
                        Recommended Actions
                      </p>
                      {expandedSections.actions ? (
                        <ChevronUp className="h-4 w-4 text-orange-300" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-orange-300" />
                      )}
                    </button>
                    {expandedSections.actions && (
                      <div className="bg-slate-900/60 border border-orange-500/30 rounded p-3 backdrop-blur-sm">
                        <ul className="space-y-2">
                          {metric.explanation.recruiter_actions.map((action: string, idx: number) => (
                            <li key={idx} className="text-sm text-slate-200 flex items-start gap-2">
                              <span className="text-orange-400 font-bold flex-shrink-0 mt-0.5">✓</span>
                              <span>{action}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {metric.explanation.dashboard_recommendation && (
                  <div className={`mt-3 p-3 rounded backdrop-blur-sm ${
                    metric.fairness_assessment === 'Violation' 
                      ? 'bg-red-950/30 border border-red-500/30' 
                      : 'bg-amber-950/30 border border-amber-500/30'
                  }`}>
                    <p className={`text-sm font-medium ${
                      metric.fairness_assessment === 'Violation' ? 'text-red-300' : 'text-amber-300'
                    }`}>
                      Recommendation: {metric.explanation.dashboard_recommendation}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Visualization */}
        <div className="mb-6">
          {vizType === 'bar' && typeof metric.values === 'object' && (
            <BarChartVisualization data={metric.values} />
          )}
          {vizType === 'scatter' && typeof metric.values === 'object' && (
            <ScatterPlotVisualization data={metric.values} />
          )}
          {vizType === 'metric' && <MetricValueDisplay value={metric.values} />}
          {vizType === 'heatmap' && typeof metric.values === 'object' && (
            <HeatmapVisualization data={metric.values as Record<string, number[]>} bins={vizData?.bins} />
          )}
          {!vizType && <MetricValueDisplay value={metric.values} />}
        </div>

        {/* Additional Information (collapsed for problematic metrics) */}
        <div className={`space-y-4 border-t pt-4 ${isProblematic ? 'text-sm' : ''}`}>
          {!isProblematic && metric.explanation.what_this_means && (
            <div>
              <h4 className="font-semibold text-sm mb-2">What This Means</h4>
              <p className="text-sm text-gray-700">{metric.explanation.what_this_means}</p>
            </div>
          )}

          <div>
            <h4 className="font-semibold text-sm mb-2 text-slate-200">Interpretation</h4>
            <p className="text-sm text-slate-300">{metric.explanation.interpretation}</p>
          </div>

          <div>
            <h4 className="font-semibold text-sm mb-2 text-slate-200">Context</h4>
            <p className="text-sm text-slate-300">{metric.explanation.context}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});
