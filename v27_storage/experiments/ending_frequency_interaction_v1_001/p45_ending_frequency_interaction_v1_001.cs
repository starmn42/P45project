using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

public static class EndingFrequencyV1
{
    const int Latest = 1238, Start = 201, NSim = 100000;
    const ulong MasterSeed = 4447818083767349720UL;
    const string ProtocolSha = "3db9d2fb4c82f1d858f49369da5ea8bfbc3268017528a4b25b903dee64489de1";
    const string DataSha = "1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8";

    struct Rng {
        ulong s;
        public Rng(ulong seed) { s=seed; }
        ulong Next64(){ s += 0x9E3779B97F4A7C15UL; ulong z=s; z=(z^(z>>30))*0xBF58476D1CE4E5B9UL; z=(z^(z>>27))*0x94D049BB133111EBUL; return z^(z>>31); }
        public int NextInt(int bound){ ulong limit=ulong.MaxValue-(ulong.MaxValue%(ulong)bound); ulong x; do{x=Next64();}while(x>=limit); return (int)(x%(ulong)bound); }
    }
    sealed class Target {
        public int Round, Z, K, Q2, RawRank2;
        public int[] CandidateQ2;
    }
    static string Sha(string path){ using(var h=SHA256.Create()) using(var f=File.OpenRead(path)) return BitConverter.ToString(h.ComputeHash(f)).Replace("-","").ToLowerInvariant(); }
    static void Draw(ref Rng rng,int[] a){ for(int i=0;i<6;i++){ int x; bool used; do{x=rng.NextInt(45); used=false; for(int j=0;j<i;j++)if(a[j]==x){used=true;break;}}while(used); a[i]=x; } }
    static int BuildCandidates(int[] prev,int[] list){ bool[] endings=new bool[10]; bool[] excluded=new bool[45]; for(int i=0;i<6;i++){endings[(prev[i]+1)%10]=true;excluded[prev[i]]=true;} int z=0; for(int n=0;n<45;n++)if(endings[(n+1)%10]&&!excluded[n])list[z++]=n; return z; }
    static int Q2For(int n,int[] cand,int z,int[] freq,out int rank2){ int less=0,equalOther=0; for(int j=0;j<z;j++){int m=cand[j];if(freq[m]<freq[n])less++;else if(m!=n&&freq[m]==freq[n])equalOther++;} rank2=2+2*less+equalOther; return rank2-(z+1); }
    static long SimulateOne(int sim){ Rng rng=new Rng(MasterSeed+0xD1B54A32D192ED03UL*(ulong)(sim+1)); int[] freq=new int[45],prev=new int[6],cur=new int[6],cand=new int[45]; Draw(ref rng,prev); for(int x=0;x<6;x++)freq[prev[x]]++; for(int r=2;r<=200;r++){Draw(ref rng,cur);for(int x=0;x<6;x++)freq[cur[x]]++;var t=prev;prev=cur;cur=t;} long totalQ2=0; for(int r=Start;r<=Latest;r++){int z=BuildCandidates(prev,cand);Draw(ref rng,cur);for(int i=0;i<6;i++){int n=cur[i],dummy;if(Array.IndexOf(cand,n,0,z)>=0)totalQ2+=Q2For(n,cand,z,freq,out dummy);}for(int i=0;i<6;i++)freq[cur[i]]++;var t=prev;prev=cur;cur=t;} return totalQ2; }
    static long ConditionalOne(int sim,List<Target> targets){ Rng rng=new Rng(MasterSeed^0xA0761D6478BD642FUL^(0xE7037ED1A0B428DBUL*(ulong)(sim+1))); long sum=0; int[] picked=new int[6]; foreach(var t in targets){for(int j=0;j<t.K;j++){int x;bool used;do{x=rng.NextInt(t.Z);used=false;for(int u=0;u<j;u++)if(picked[u]==x){used=true;break;}}while(used);picked[j]=x;sum+=t.CandidateQ2[x];}}return sum; }
    static Dictionary<string,string> Period(List<Target> t,int from,int count){var s=t.Skip(from).Take(count).ToList();long q=s.Sum(x=>(long)x.Q2);long raw=s.Sum(x=>(long)x.RawRank2);int hits=s.Sum(x=>x.K),ex=s.Sum(x=>x.Z);return new Dictionary<string,string>{{"n",s.Count.ToString()},{"score",(q/2.0).ToString("R",CultureInfo.InvariantCulture)},{"mean_round",(q/2.0/s.Count).ToString("R",CultureInfo.InvariantCulture)},{"hits",hits.ToString()},{"exposures",ex.ToString()},{"mean_hit_centered",hits>0?(q/2.0/hits).ToString("R",CultureInfo.InvariantCulture):"NA"},{"mean_hit_raw_rank",hits>0?(raw/2.0/hits).ToString("R",CultureInfo.InvariantCulture):"NA"}};}
    static string J(Dictionary<string,string>d,string k)=>d[k];

    public static void Run(string root)
    {
        string outDir=Path.Combine(root,"v27_storage","experiments","ending_frequency_interaction_v1_001");
        string data=Path.Combine(root,"v27_storage","audits","current_1239_predraw_rerun_001","STAGING_CONTIGUOUS_DRAW_1_1238.csv");
        string protocol=Path.Combine(outDir,"P45_ENDING_FREQUENCY_INTERACTION_V1_PROTOCOL_LOCKED_001.md");
        if(Sha(data)!=DataSha||Sha(protocol)!=ProtocolSha)throw new Exception("LOCK_OR_DATA_HASH_MISMATCH");
        var lines=File.ReadAllLines(data); if(lines.Length!=Latest+1)throw new Exception("ROW_COUNT_FAIL");
        int[][] draws=new int[Latest][]; int[] bonus=new int[Latest];
        for(int i=1;i<lines.Length;i++){var p=lines[i].Split(',');int round=int.Parse(p[0]);if(round!=i)throw new Exception("CONTINUITY_FAIL");draws[i-1]=new int[6];var seen=new bool[45];for(int j=0;j<6;j++){int n=int.Parse(p[j+2]);if(n<1||n>45||seen[n-1])throw new Exception("MAIN_FAIL");seen[n-1]=true;draws[i-1][j]=n-1;}bonus[i-1]=int.Parse(p[8]);if(bonus[i-1]<1||bonus[i-1]>45||seen[bonus[i-1]-1])throw new Exception("BONUS_FAIL");}
        int[] freq=new int[45];for(int r=0;r<200;r++)foreach(int n in draws[r])freq[n]++;
        var targets=new List<Target>();var trace=new StringBuilder("target_round,candidate_size,candidate_hits,round_score,raw_rank_sum,centered_score_x2,future_leakage_flag\n");
        for(int r=Start;r<=Latest;r++){int[] cand=new int[45];int z=BuildCandidates(draws[r-2],cand);int[] qAll=new int[z];for(int j=0;j<z;j++){int rank2;qAll[j]=Q2For(cand[j],cand,z,freq,out rank2);}if(qAll.Sum()!=0)throw new Exception("CENTER_FAIL");int k=0,q2=0,raw2=0;foreach(int n in draws[r-1]){int idx=Array.IndexOf(cand,n,0,z);if(idx>=0){int rank2;k++;q2+=Q2For(n,cand,z,freq,out rank2);raw2+=rank2;}}targets.Add(new Target{Round=r,Z=z,K=k,Q2=q2,RawRank2=raw2,CandidateQ2=qAll});trace.AppendFormat(CultureInfo.InvariantCulture,"{0},{1},{2},{3:R},{4:R},{5},0\n",r,z,k,q2/2.0,raw2/2.0,q2);foreach(int n in draws[r-1])freq[n]++;}
        string tracePath=Path.Combine(outDir,"P45_ENDING_FREQUENCY_INTERACTION_V1_TRACE_001.csv");File.WriteAllText(tracePath,trace.ToString(),new UTF8Encoding(false));
        long obsQ2=targets.Sum(x=>(long)x.Q2); long[] mc=new long[NSim];Parallel.For(0,NSim,i=>mc[i]=SimulateOne(i));long mcExtreme=mc.LongCount(x=>Math.Abs(x)>=Math.Abs(obsQ2));
        long[] cond=new long[NSim];Parallel.For(0,NSim,i=>cond[i]=ConditionalOne(i,targets));long condExtreme=cond.LongCount(x=>Math.Abs(x)>=Math.Abs(obsQ2));
        int nT=targets.Count,cut=(nT+1)/2;var full=Period(targets,0,nT);var first=Period(targets,0,cut);var second=Period(targets,cut,nT-cut);var r100=Period(targets,nT-100,100);var r50=Period(targets,nT-50,50);var r20=Period(targets,nT-20,20);
        double pmc=(1.0+mcExtreme)/(NSim+1.0),pcond=(1.0+condExtreme)/(NSim+1.0);double fscore=double.Parse(J(first,"score"),CultureInfo.InvariantCulture),sscore=double.Parse(J(second,"score"),CultureInfo.InvariantCulture);bool conflict=fscore*sscore<0&&Math.Abs(fscore)>Math.Abs(obsQ2/4.0)&&Math.Abs(sscore)>Math.Abs(obsQ2/4.0);string judgment=pmc<=.05&&pcond<=.05&&!conflict?"STRONG_INTERACTION_CANDIDATE":pmc>.05&&pmc<=.10&&!conflict?"INTERESTING_WATCHLIST":"FAILED_NOT_INTERESTING";
        int exposures=targets.Sum(x=>x.Z),hits=targets.Sum(x=>x.K);double rate=(double)hits/exposures,rd=rate-6.0/45.0;
        var sb=new StringBuilder();Action<string,object> add=(k,v)=>sb.Append(k).Append('=').Append(Convert.ToString(v,CultureInfo.InvariantCulture)).Append('\n');add("PRECHECK","PASS");add("LATEST",Latest);add("DATA_SHA",DataSha);add("PROTOCOL_SHA",ProtocolSha);add("SEED",MasterSeed);add("NSIM",NSim);add("EVALUATED",nT);add("EXPOSURES",exposures);add("HITS",hits);add("HIT_RATE",rate.ToString("R",CultureInfo.InvariantCulture));add("EXPECTED_RATE",(6.0/45.0).ToString("R",CultureInfo.InvariantCulture));add("RATE_DIFFERENCE",rd.ToString("R",CultureInfo.InvariantCulture));add("TOTAL_SCORE",(obsQ2/2.0).ToString("R",CultureInfo.InvariantCulture));add("MEAN_HIT_CENTERED",(obsQ2/2.0/hits).ToString("R",CultureInfo.InvariantCulture));add("MEAN_HIT_RAW_RANK",(targets.Sum(x=>(long)x.RawRank2)/2.0/hits).ToString("R",CultureInfo.InvariantCulture));add("PRIMARY_EXTREME",mcExtreme);add("PRIMARY_P",pmc.ToString("R",CultureInfo.InvariantCulture));add("CONDITIONAL_EXTREME",condExtreme);add("CONDITIONAL_P",pcond.ToString("R",CultureInfo.InvariantCulture));add("JUDGMENT",judgment);add("CONFLICT",conflict);foreach(var pair in new[]{Tuple.Create("FULL",full),Tuple.Create("FIRST",first),Tuple.Create("SECOND",second),Tuple.Create("RECENT100",r100),Tuple.Create("RECENT50",r50),Tuple.Create("RECENT20",r20)})foreach(var kv in pair.Item2)add(pair.Item1+"_"+kv.Key.ToUpperInvariant(),kv.Value);add("MC_NULL_MEAN_SCORE",(mc.Average(x=>(double)x)/2.0).ToString("R",CultureInfo.InvariantCulture));add("CONDITIONAL_NULL_MEAN_SCORE",(cond.Average(x=>(double)x)/2.0).ToString("R",CultureInfo.InvariantCulture));add("FUTURE_LEAKAGE",0);add("OFFICIAL_PROTECTED_CHANGES",0);add("EXP006_FINAL","FAILED");add("EXP013_FINAL","FAILED_EARLY");add("EXP017","NOT_CREATED");File.WriteAllText(Path.Combine(outDir,"COMPUTATION_OUTPUT_001.txt"),sb.ToString(),new UTF8Encoding(false));Console.WriteLine(sb.ToString());
    }
}
