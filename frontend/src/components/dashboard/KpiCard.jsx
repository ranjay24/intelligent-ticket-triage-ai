import {
    TrendingUp,
    TrendingDown
} from "lucide-react";

function KpiCard({

    title,
    value,
    icon,
    color,
    trend,
    trendUp = true

}) {

    return (

        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 hover:shadow-lg transition">

            <div className="flex items-center justify-between">

                <div>

                    <p className="text-xs uppercase tracking-wider text-slate-500 font-semibold">

                        {title}

                    </p>

                    <h2 className={`text-4xl font-bold mt-2 ${color}`}>

                        {value}

                    </h2>

                </div>

                <div className={`w-14 h-14 rounded-xl flex items-center justify-center ${color.replace("text", "bg")}/10`}>

                    {icon}

                </div>

            </div>

            <div className="flex items-center gap-2 mt-5">

                {

                    trendUp

                        ?

                        <TrendingUp
                            size={18}
                            className="text-green-600"
                        />

                        :

                        <TrendingDown
                            size={18}
                            className="text-red-600"
                        />

                }

                <span className="text-sm text-slate-500">

                    {trend}

                </span>

            </div>

        </div>

    );

}

export default KpiCard;