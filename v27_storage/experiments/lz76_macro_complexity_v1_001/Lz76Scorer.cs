using System;
using System.Collections.Concurrent;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

public sealed class Workspace
{
    public readonly int[] Next0 = new int[9001];
    public readonly int[] Next1 = new int[9001];
    public readonly int[] Link = new int[9001];
    public readonly int[] Length = new int[9001];

    public void InitializeState(int state)
    {
        Next0[state] = -1;
        Next1[state] = -1;
        Link[state] = -1;
        Length[state] = 0;
    }
}

public static class Lz76Scorer
{
    private const int WindowBits = 4500;
    private const int HistoryBits = 1238 * 45;
    private const int WindowCount = 1139;

    private static int Lz76Count(byte[] data, int offset, Workspace w)
    {
        int size = 1;
        int last = 0;
        w.InitializeState(0);

        Action<byte> extend = ch =>
        {
            int cur = size++;
            w.InitializeState(cur);
            w.Length[cur] = w.Length[last] + 1;
            int p = last;
            int[] transitions = ch != 0 ? w.Next1 : w.Next0;
            while (p >= 0 && transitions[p] < 0)
            {
                transitions[p] = cur;
                p = w.Link[p];
            }
            if (p < 0)
            {
                w.Link[cur] = 0;
            }
            else
            {
                int q = transitions[p];
                if (w.Length[p] + 1 == w.Length[q])
                {
                    w.Link[cur] = q;
                }
                else
                {
                    int clone = size++;
                    w.InitializeState(clone);
                    w.Length[clone] = w.Length[p] + 1;
                    w.Link[clone] = w.Link[q];
                    w.Next0[clone] = w.Next0[q];
                    w.Next1[clone] = w.Next1[q];
                    while (p >= 0 && transitions[p] == q)
                    {
                        transitions[p] = clone;
                        p = w.Link[p];
                    }
                    w.Link[q] = clone;
                    w.Link[cur] = clone;
                }
            }
            last = cur;
        };

        int pos = 0;
        int count = 0;
        while (pos < WindowBits)
        {
            int state = 0;
            int end = pos;
            while (end < WindowBits)
            {
                byte bit = data[offset + end];
                int next = bit != 0 ? w.Next1[state] : w.Next0[state];
                if (next < 0) break;
                state = next;
                end++;
            }
            int phraseLength = end < WindowBits ? end - pos + 1 : WindowBits - pos;
            count++;
            for (int index = pos; index < pos + phraseLength; index++) extend(data[offset + index]);
            pos += phraseLength;
        }
        return count;
    }

    private static double? Correlation(byte[] states)
    {
        int n = states.Length - 1;
        long sx = 0, sy = 0, sxy = 0;
        for (int i = 0; i < n; i++)
        {
            int x = states[i];
            int y = states[i + 1];
            sx += x;
            sy += y;
            sxy += x * y;
        }
        long vx = n * sx - sx * sx;
        long vy = n * sy - sy * sy;
        if (vx == 0 || vy == 0) return null;
        return (n * sxy - sx * sy) / Math.Sqrt((double)vx * vy);
    }

    private static string Arg(string[] args, string name)
    {
        string prefix = name + "=";
        string value = args.FirstOrDefault(a => a.StartsWith(prefix, StringComparison.Ordinal));
        if (value == null) throw new ArgumentException("Missing " + name);
        return value.Substring(prefix.Length);
    }

    public static int Main(string[] args)
    {
        string mode = Arg(args, "mode");
        string input = Arg(args, "input");
        string output = Arg(args, "output");
        int rows = int.Parse(Arg(args, "rows"), CultureInfo.InvariantCulture);
        int workers = int.Parse(Arg(args, "workers"), CultureInfo.InvariantCulture);
        int qCount = mode == "histories" ? int.Parse(Arg(args, "qCount"), CultureInfo.InvariantCulture) : 0;
        byte[] data = File.ReadAllBytes(input);
        long expected = (long)rows * (mode == "threshold" ? WindowBits : HistoryBits);
        if (data.LongLength != expected) throw new InvalidDataException("binary input size mismatch");
        var options = new ParallelOptions { MaxDegreeOfParallelism = workers };
        var local = new ThreadLocal<Workspace>(() => new Workspace());

        if (mode == "threshold")
        {
            short[] counts = new short[rows];
            Parallel.For(0, rows, options, row =>
            {
                counts[row] = (short)Lz76Count(data, row * WindowBits, local.Value);
            });
            using (var writer = new StreamWriter(output, false, new UTF8Encoding(false)))
            {
                writer.Write("{\"mode\":\"threshold\",\"rows\":");
                writer.Write(rows);
                writer.Write(",\"counts\":[");
                for (int i = 0; i < rows; i++) { if (i > 0) writer.Write(','); writer.Write(counts[i]); }
                writer.Write("]}");
            }
        }
        else
        {
            double[] occupancy = new double[rows];
            double[] autocorr = new double[rows];
            int[] stateCounts = new int[rows];
            byte[] estimable = new byte[rows];
            Parallel.For(0, rows, options, row =>
            {
                var states = new byte[WindowCount];
                int baseOffset = row * HistoryBits;
                int countA = 0;
                Workspace w = local.Value;
                for (int window = 0; window < WindowCount; window++)
                {
                    int count = Lz76Count(data, baseOffset + window * 45, w);
                    byte state = count <= qCount ? (byte)1 : (byte)0;
                    states[window] = state;
                    countA += state;
                }
                double? corr = Correlation(states);
                stateCounts[row] = countA;
                occupancy[row] = (double)countA / WindowCount;
                if (corr.HasValue && !double.IsNaN(corr.Value) && !double.IsInfinity(corr.Value))
                {
                    autocorr[row] = corr.Value;
                    estimable[row] = 1;
                }
            });
            using (var writer = new StreamWriter(output, false, new UTF8Encoding(false)))
            {
                writer.Write("{\"mode\":\"histories\",\"rows\":"); writer.Write(rows);
                writer.Write(",\"qCount\":"); writer.Write(qCount);
                writer.Write(",\"occupancy\":[");
                for (int i = 0; i < rows; i++) { if (i > 0) writer.Write(','); writer.Write(occupancy[i].ToString("R", CultureInfo.InvariantCulture)); }
                writer.Write("],\"autocorr\":[");
                for (int i = 0; i < rows; i++) { if (i > 0) writer.Write(','); writer.Write(autocorr[i].ToString("R", CultureInfo.InvariantCulture)); }
                writer.Write("],\"stateCounts\":[");
                for (int i = 0; i < rows; i++) { if (i > 0) writer.Write(','); writer.Write(stateCounts[i]); }
                writer.Write("],\"estimable\":[");
                for (int i = 0; i < rows; i++) { if (i > 0) writer.Write(','); writer.Write(estimable[i]); }
                writer.Write("]}");
            }
        }
        return 0;
    }
}
