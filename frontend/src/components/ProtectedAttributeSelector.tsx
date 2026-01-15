
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { useStore } from '@/lib/store';

export function ProtectedAttributeSelector() {
  const { protectedAttribute, setProtectedAttribute, currentDataset } = useStore();

  if (!currentDataset) {
    return null;
  }

  const hasGender = currentDataset.column_names.includes('gender');
  const hasAgeGroup = currentDataset.has_age_group || currentDataset.column_names.includes('age_group');

  return (
    <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
      <CardHeader>
        <CardTitle className="text-slate-100">Protected Attribute</CardTitle>
        <CardDescription className="text-slate-400">
          Select the demographic attribute to analyze for fairness
        </CardDescription>
      </CardHeader>
      <CardContent>
        <RadioGroup value={protectedAttribute} onValueChange={setProtectedAttribute}>
          {hasGender && (
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="gender" id="gender" />
              <Label htmlFor="gender" className="cursor-pointer">
                Gender
              </Label>
            </div>
          )}
          {hasAgeGroup && (
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="age_group" id="age_group" />
              <Label htmlFor="age_group" className="cursor-pointer">
                Age Group
              </Label>
            </div>
          )}
        </RadioGroup>

        {!hasGender && !hasAgeGroup && (
          <p className="text-sm text-red-600">
            No protected attributes found. Dataset must include 'gender' or 'age'/'age_group' columns.
          </p>
        )}

        <div className="mt-4 p-3 bg-slate-800/50 border border-slate-600/50 rounded-lg backdrop-blur-sm">
          <p className="text-xs text-slate-300">
            <strong className="text-orange-400">Current selection:</strong> {protectedAttribute}
          </p>
          <p className="text-xs text-slate-400 mt-1">
            All fairness metrics will be calculated across groups defined by this attribute.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
