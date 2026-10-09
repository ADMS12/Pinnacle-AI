import { Provider } from '@nestjs/common';
import { SOLVER_ADAPTER } from './solver-adapter';
import { TimefoldAdapter } from './timefold.adapter';
import { SelfHostedAdapter } from './self-hosted.adapter';

/** Swap backends with one env var. Nothing above the adapter changes. */
export const SolverProvider: Provider = {
  provide: SOLVER_ADAPTER,
  useFactory: () =>
    process.env.SOLVER_BACKEND === 'self_hosted' ? new SelfHostedAdapter() : new TimefoldAdapter(),
};
